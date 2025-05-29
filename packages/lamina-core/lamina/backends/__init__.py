# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
AI Backend Integrations for Lamina Core

This module provides pluggable AI backend support for multiple providers
including Ollama, HuggingFace, and others.
"""

from .base import BaseBackend
from .ollama import OllamaBackend

# Optional backends with graceful import handling
try:
    from .huggingface import HuggingFaceBackend

    HUGGINGFACE_AVAILABLE = True
except ImportError:
    HuggingFaceBackend = None
    HUGGINGFACE_AVAILABLE = False


class MockBackend(BaseBackend):
    """Mock backend for testing and demonstrations."""

    def __init__(self, config: dict):
        super().__init__(config)
        self.model_name = config.get("model", "mock-model")

    async def generate(self, messages, stream=True):
        """Generate mock response."""
        import asyncio

        await asyncio.sleep(0.2)  # Simulate processing time
        response = f"Mock response from {self.model_name}: I understand your request and am providing a thoughtful response."
        if stream:
            for chunk in response.split():
                yield chunk + " "
        else:
            yield response

    async def is_available(self):
        return True

    async def load_model(self):
        return True

    async def unload_model(self):
        return True


# Backend registry
BACKENDS = {
    "ollama": OllamaBackend,
    "mock": MockBackend,
}

# Add optional backends if available
if HUGGINGFACE_AVAILABLE:
    BACKENDS["huggingface"] = HuggingFaceBackend


def get_backend(provider: str, config: dict = None) -> BaseBackend:
    """Get an AI backend instance for the specified provider."""
    if provider not in BACKENDS:
        available = ", ".join(BACKENDS.keys())
        raise ValueError(f"Unknown backend '{provider}'. Available: {available}")

    backend_class = BACKENDS[provider]
    return backend_class(config or {})


def list_backends() -> list[str]:
    """List all available backend providers."""
    return list(BACKENDS.keys())


__all__ = [
    "BaseBackend",
    "OllamaBackend",
    "HuggingFaceBackend",
    "get_backend",
    "list_backends",
    "BACKENDS",
]
