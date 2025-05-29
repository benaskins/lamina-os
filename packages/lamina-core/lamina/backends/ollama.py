"""
Ollama Backend for Local Model Serving

This backend provides AI inference using Ollama for local model serving.
"""

import json
import logging
from typing import Any, AsyncGenerator, Dict, List

import aiohttp

from .base import BaseBackend, Message

logger = logging.getLogger(__name__)


class OllamaBackend(BaseBackend):
    """Ollama backend for local model serving"""

    def __init__(self, config: Dict[str, Any]):
        """Initialize Ollama backend with configuration"""
        super().__init__(config)

        self.base_url = config.get("base_url", "localhost:11434")
        self.endpoints = config.get("endpoints", {})
        self.timeout = config.get("timeout", 30)

        # Ensure base_url has protocol
        if not self.base_url.startswith(("http://", "https://")):
            self.base_url = f"http://{self.base_url}"

        logger.info(f"Ollama backend initialized for model: {self.model_name}")
        logger.info(f"Base URL: {self.base_url}")

    async def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                async with session.get(f"{self.base_url}/api/tags") as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Ollama not available: {e}")
            return False

    async def load_model(self) -> bool:
        """Load model in Ollama (models are loaded on-demand)"""
        # Ollama loads models on-demand, so we just check if it's available
        return await self.is_available()

    async def unload_model(self) -> bool:
        """Unload model (Ollama manages this automatically)"""
        # Ollama manages model lifecycle automatically
        return True

    async def generate(
        self, messages: List[Message], stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """Generate response using Ollama"""
        try:
            # Get chat endpoint
            chat_endpoint = self.endpoints.get("chat", "/api/chat")
            url = f"{self.base_url}{chat_endpoint}"

            # Convert messages to Ollama format
            ollama_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
                if msg.role != "system"  # Ollama handles system messages differently
            ]

            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": ollama_messages,
                "stream": stream,
                **self.parameters,
            }

            logger.debug(f"Sending request to Ollama: {url}")

            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as session:
                async with session.post(url, json=payload) as response:
                    if not response.ok:
                        error_text = await response.text()
                        logger.error(f"Ollama error {response.status}: {error_text}")
                        yield f"Error: {error_text}"
                        return

                    if stream:
                        # Handle streaming response
                        async for line in response.content:
                            if line:
                                try:
                                    chunk = json.loads(line.decode("utf-8"))
                                    text = chunk.get("message", {}).get("content", "")
                                    if text:
                                        yield text
                                except json.JSONDecodeError:
                                    continue
                    else:
                        # Handle non-streaming response
                        try:
                            data = await response.json()
                            text = data.get("message", {}).get("content", "")
                            if text:
                                yield text
                        except Exception as e:
                            logger.error(f"Failed to parse Ollama response: {e}")
                            yield f"Error: Failed to parse response"

        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            yield f"Error: {str(e)}"

    def get_model_info(self) -> Dict[str, Any]:
        """Get Ollama model information"""
        info = super().get_model_info()
        info.update(
            {
                "base_url": self.base_url,
                "timeout": self.timeout,
                "endpoints": self.endpoints,
            }
        )
        return info
