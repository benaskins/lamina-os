"""
AI Backend Integrations for Lamina Core

This module provides pluggable AI backend support for multiple providers
including Ollama, HuggingFace, and others.
"""

from .base import BaseBackend
from .ollama import OllamaBackend
from .huggingface import HuggingFaceBackend

# Backend registry
BACKENDS = {
    "ollama": OllamaBackend,
    "huggingface": HuggingFaceBackend,
}


def get_backend(provider: str, **kwargs) -> BaseBackend:
    """Get an AI backend instance for the specified provider."""
    if provider not in BACKENDS:
        available = ", ".join(BACKENDS.keys())
        raise ValueError(f"Unknown backend '{provider}'. Available: {available}")
    
    backend_class = BACKENDS[provider]
    return backend_class(**kwargs)


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
