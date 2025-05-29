"""
Lamina LLM Serve - Centralized model caching and serving layer

This package provides unified access to language models for Lamina OS,
handling model discovery, caching, and backend routing.
"""

__version__ = "0.1.0"

from .model_manager import ModelManager
from .backends import get_backend_for_model
from .server import LLMServer

__all__ = ["ModelManager", "get_backend_for_model", "LLMServer"]