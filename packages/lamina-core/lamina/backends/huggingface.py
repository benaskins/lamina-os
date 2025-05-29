# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
HuggingFace Transformers Backend for Local Model Inference

This backend provides local AI inference using HuggingFace Transformers library,
supporting various models, quantization options, and device management.
"""

import asyncio
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

import torch
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TextStreamer,
)

from .base import BaseBackend, Message

logger = logging.getLogger(__name__)


class HuggingFaceBackend(BaseBackend):
    """HuggingFace Transformers backend for local inference"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize HuggingFace backend with configuration"""
        super().__init__(config)

        self.device = self._determine_device()
        self.torch_dtype = self._determine_torch_dtype()
        self.quantization_config = self._get_quantization_config()

        self.tokenizer: Optional[AutoTokenizer] = None
        self.model: Optional[AutoModelForCausalLM] = None
        self.is_loaded = False

        logger.info(f"HuggingFace backend initialized for model: {self.model_name}")
        logger.info(f"Device: {self.device}, Torch dtype: {self.torch_dtype}")

    def _determine_device(self) -> str:
        """Determine the best device to use"""
        device_config = self.config.get("device", "auto")

        if device_config == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                return "mps"  # Apple Silicon
            else:
                return "cpu"

        return device_config

    def _determine_torch_dtype(self) -> torch.dtype:
        """Determine the torch dtype to use"""
        dtype_config = self.config.get("torch_dtype", "auto")

        if dtype_config == "auto":
            if self.device == "cuda":
                return torch.float16  # Use half precision on GPU
            else:
                return torch.float32  # Use full precision on CPU/MPS

        dtype_map = {
            "float16": torch.float16,
            "bfloat16": torch.bfloat16,
            "float32": torch.float32,
        }

        return dtype_map.get(dtype_config, torch.float32)

    def _get_quantization_config(self) -> Optional[BitsAndBytesConfig]:
        """Get quantization configuration if enabled"""
        quant_config = self.config.get("quantization", {})

        if quant_config.get("load_in_4bit", False):
            return BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=getattr(
                    torch, quant_config.get("bnb_4bit_compute_dtype", "float16")
                ),
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
            )
        elif quant_config.get("load_in_8bit", False):
            return BitsAndBytesConfig(load_in_8bit=True)

        return None

    async def load_model(self) -> bool:
        """Load the HuggingFace model and tokenizer"""
        if self.is_loaded:
            return True

        try:
            logger.info(f"Loading HuggingFace model: {self.model_name}")

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_name, trust_remote_code=True
            )

            # Set pad token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Prepare model loading arguments
            model_kwargs = {
                "torch_dtype": self.torch_dtype,
                "trust_remote_code": True,
                "low_cpu_mem_usage": True,
            }

            # Add quantization config if specified
            if self.quantization_config:
                model_kwargs["quantization_config"] = self.quantization_config
                logger.info("Loading model with quantization")
            else:
                model_kwargs["device_map"] = self.device

            # Load model
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name, **model_kwargs
            )

            # Move to device if not using quantization
            if not self.quantization_config and self.device != "auto":
                self.model = self.model.to(self.device)

            self.is_loaded = True
            logger.info(f"Successfully loaded model on {self.device}")
            return True

        except Exception as e:
            logger.error(f"Failed to load HuggingFace model: {e}")
            return False

    async def unload_model(self) -> bool:
        """Unload the model to free memory"""
        try:
            if self.model is not None:
                del self.model
                self.model = None

            if self.tokenizer is not None:
                del self.tokenizer
                self.tokenizer = None

            # Clear GPU cache if using CUDA
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            self.is_loaded = False
            logger.info("Model unloaded successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to unload model: {e}")
            return False

    async def is_available(self) -> bool:
        """Check if the backend is available"""
        try:
            # Check if transformers is available
            import transformers

            # Check if model is loaded or can be loaded
            if not self.is_loaded:
                return await self.load_model()

            return True

        except ImportError:
            logger.error("HuggingFace Transformers not installed")
            return False
        except Exception as e:
            logger.error(f"HuggingFace backend not available: {e}")
            return False

    async def generate(
        self, messages: List[Message], stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate response using HuggingFace model"""
        if not self.is_loaded:
            if not await self.load_model():
                yield "Error: Failed to load model"
                return

        try:
            # Format messages into a prompt
            prompt = self._format_messages(messages)

            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.tokenizer.model_max_length
                - self.parameters.get("max_new_tokens", 2048),
            )

            # Move inputs to device
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

            # Prepare generation parameters
            generation_params = {
                **inputs,
                "max_new_tokens": self.parameters.get("max_new_tokens", 2048),
                "do_sample": self.parameters.get("do_sample", True),
                "temperature": self.parameters.get("temperature", 0.7),
                "top_p": self.parameters.get("top_p", 0.9),
                "top_k": self.parameters.get("top_k", 50),
                "repetition_penalty": self.parameters.get("repetition_penalty", 1.1),
                "pad_token_id": self.tokenizer.pad_token_id,
                "eos_token_id": self.tokenizer.eos_token_id,
                "return_dict_in_generate": True,
                "output_scores": False,
            }

            if stream:
                # Streaming generation
                async for chunk in self._generate_streaming(
                    generation_params, inputs["input_ids"].shape[1]
                ):
                    yield chunk
            else:
                # Non-streaming generation
                response = await self._generate_complete(
                    generation_params, inputs["input_ids"].shape[1]
                )
                yield response

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            yield f"Error: {str(e)}"

    def _format_messages(self, messages: List[Message]) -> str:
        """Format messages into a prompt string"""
        # Simple chat template - can be enhanced based on model requirements
        formatted_parts = []

        for message in messages:
            if message.role == "system":
                formatted_parts.append(f"System: {message.content}")
            elif message.role == "user":
                formatted_parts.append(f"User: {message.content}")
            elif message.role == "assistant":
                formatted_parts.append(f"Assistant: {message.content}")

        # Add assistant prompt for response
        formatted_parts.append("Assistant:")

        return "\n".join(formatted_parts)

    async def _generate_streaming(
        self, generation_params: Dict[str, Any], input_length: int
    ) -> AsyncGenerator[str, None]:
        """Generate response with streaming"""
        try:
            # Use a simple approach: generate tokens one by one
            # This is a simplified streaming implementation

            # For now, generate complete response and yield in chunks
            # A more sophisticated implementation would use custom generation loop
            with torch.no_grad():
                outputs = self.model.generate(**generation_params)

            # Decode only the new tokens
            new_tokens = outputs.sequences[0][input_length:]
            response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)

            # Yield response in chunks to simulate streaming
            chunk_size = 10  # Characters per chunk
            for i in range(0, len(response), chunk_size):
                chunk = response[i : i + chunk_size]
                yield chunk
                await asyncio.sleep(0.01)  # Small delay to simulate streaming

        except Exception as e:
            logger.error(f"Streaming generation failed: {e}")
            yield f"Error: {str(e)}"

    async def _generate_complete(
        self, generation_params: Dict[str, Any], input_length: int
    ) -> str:
        """Generate complete response"""
        try:
            with torch.no_grad():
                outputs = self.model.generate(**generation_params)

            # Decode only the new tokens
            new_tokens = outputs.sequences[0][input_length:]
            response = self.tokenizer.decode(new_tokens, skip_special_tokens=True)

            return response.strip()

        except Exception as e:
            logger.error(f"Complete generation failed: {e}")
            return f"Error: {str(e)}"

    def get_model_info(self) -> Dict[str, Any]:
        """Get detailed model information"""
        info = super().get_model_info()
        info.update(
            {
                "device": self.device,
                "torch_dtype": str(self.torch_dtype),
                "is_loaded": self.is_loaded,
                "quantization": self.quantization_config is not None,
                "model_size": self._get_model_size() if self.is_loaded else "Unknown",
            }
        )
        return info

    def _get_model_size(self) -> str:
        """Get approximate model size"""
        if not self.model:
            return "Unknown"

        try:
            param_count = sum(p.numel() for p in self.model.parameters())

            if param_count > 1e9:
                return f"{param_count / 1e9:.1f}B parameters"
            elif param_count > 1e6:
                return f"{param_count / 1e6:.1f}M parameters"
            else:
                return f"{param_count / 1e3:.1f}K parameters"
        except:
            return "Unknown"
