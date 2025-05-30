# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Lamina LLM Client - Direct connection to lamina-llm-serve

Simplified client that communicates with lamina-llm-serve using the OpenAI-compatible
chat completions API. No backend abstraction needed since lamina-llm-serve handles that.
"""

import logging
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

import aiohttp

logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a chat message"""

    role: str  # "user", "assistant", "system"
    content: str


class LaminaLLMClient:
    """Client that connects to lamina-llm-serve for AI model access."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the Lamina LLM client.

        Args:
            config: Configuration dictionary with:
                - base_url: URL of lamina-llm-serve instance
                - model: Model name to use
                - timeout: Request timeout in seconds (default: 60)
                - parameters: Model parameters (temperature, max_tokens, etc.)
        """
        self.config = config
        self.base_url = config.get("base_url", "http://localhost:8080").rstrip("/")
        self.model_name = config.get("model", "")
        self.timeout = config.get("timeout", 60)
        self.parameters = config.get("parameters", {})

    async def generate(
        self, messages: list[Message], stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Generate response using lamina-llm-serve's chat completions API.

        Args:
            messages: List of conversation messages
            stream: Whether to stream the response

        Yields:
            Generated text chunks or complete response
        """
        try:
            # Convert messages to OpenAI format
            openai_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": openai_messages,
                "stream": stream,
                **self.parameters,  # Include temperature, max_tokens, etc.
            }

            url = f"{self.base_url}/v1/chat/completions"
            timeout = aiohttp.ClientTimeout(total=self.timeout)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, json=payload) as response:

                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"LLM Serve error {response.status}: {error_text}")
                        yield f"Error: LLM server returned {response.status}"
                        return

                    if stream:
                        # Handle streaming response
                        async for line in response.content:
                            line_text = line.decode("utf-8").strip()
                            if line_text:
                                # For streaming, just yield the chunks as they come
                                # lamina-llm-serve handles the streaming format
                                yield line_text
                    else:
                        # Handle non-streaming response
                        response_data = await response.json()

                        # Extract content from OpenAI-format response
                        if "choices" in response_data and len(response_data["choices"]) > 0:
                            choice = response_data["choices"][0]
                            if "message" in choice and "content" in choice["message"]:
                                yield choice["message"]["content"]
                            else:
                                logger.warning("Unexpected response format from LLM serve")
                                yield str(response_data)
                        else:
                            logger.warning("No choices in response from LLM serve")
                            yield str(response_data)

        except TimeoutError:
            logger.error(f"Timeout connecting to LLM serve at {self.base_url}")
            yield "Error: Request timeout"
        except aiohttp.ClientError as e:
            logger.error(f"Connection error to LLM serve: {e}")
            yield f"Error: Connection failed - {str(e)}"
        except Exception as e:
            logger.error(f"LLM Serve generation failed: {e}")
            yield f"Error: {str(e)}"

    async def is_available(self) -> bool:
        """
        Check if lamina-llm-serve is available and responsive.

        Returns:
            True if the service is available, False otherwise
        """
        try:
            url = f"{self.base_url}/health"
            timeout = aiohttp.ClientTimeout(total=5)  # Short timeout for health check

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    return response.status == 200

        except Exception as e:
            logger.debug(f"LLM Serve not available: {e}")
            return False

    async def load_model(self) -> bool:
        """
        Ensure the model is loaded in lamina-llm-serve.

        The service handles auto-loading, so this just checks if the model exists.

        Returns:
            True if model is available, False otherwise
        """
        try:
            url = f"{self.base_url}/models/{self.model_name}"
            timeout = aiohttp.ClientTimeout(total=10)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        model_data = await response.json()
                        return model_data.get("available", False)
                    else:
                        logger.warning(f"Model {self.model_name} not found in LLM serve")
                        return False

        except Exception as e:
            logger.error(f"Error checking model {self.model_name}: {e}")
            return False

    async def unload_model(self) -> bool:
        """
        Request to stop the model in lamina-llm-serve.

        Returns:
            True if model stopped successfully, False otherwise
        """
        try:
            url = f"{self.base_url}/models/{self.model_name}/stop"
            timeout = aiohttp.ClientTimeout(total=10)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url) as response:
                    if response.status == 200:
                        logger.info(f"Model {self.model_name} stopped successfully")
                        return True
                    else:
                        logger.warning(f"Failed to stop model {self.model_name}: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"Error stopping model {self.model_name}: {e}")
            return False

    def get_model_info(self) -> dict[str, Any]:
        """Get information about the configured model."""
        return {
            "model_name": self.model_name,
            "parameters": self.parameters,
            "client": "lamina-llm-serve",
            "base_url": self.base_url,
            "timeout": self.timeout,
        }
