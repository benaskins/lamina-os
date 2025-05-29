# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Base Backend Interface for AI Providers

This module defines the abstract base class that all AI provider backends must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List


@dataclass
class Message:
    """Represents a chat message"""

    role: str  # "user", "assistant", "system"
    content: str


class BaseBackend(ABC):
    """Abstract base class for AI provider backends"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the backend with configuration

        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = config
        self.model_name = config.get("model", "")
        self.parameters = config.get("parameters", {})

    @abstractmethod
    async def generate(
        self, messages: List[Message], stream: bool = True
    ) -> AsyncGenerator[str, None]:
        """
        Generate a response from the AI model

        Args:
            messages: List of conversation messages
            stream: Whether to stream the response

        Yields:
            Generated text chunks (if streaming) or complete response
        """
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """
        Check if the backend is available and ready to use

        Returns:
            True if the backend is available, False otherwise
        """
        pass

    @abstractmethod
    async def load_model(self) -> bool:
        """
        Load the model if needed

        Returns:
            True if model loaded successfully, False otherwise
        """
        pass

    @abstractmethod
    async def unload_model(self) -> bool:
        """
        Unload the model to free resources

        Returns:
            True if model unloaded successfully, False otherwise
        """
        pass

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the loaded model

        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "parameters": self.parameters,
            "backend": self.__class__.__name__,
        }
