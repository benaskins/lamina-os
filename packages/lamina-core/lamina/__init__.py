"""
Lamina Core - Modular AI Agent Framework

A magical framework for building AI agent systems with multi-backend support,
intelligent memory, and distributed infrastructure.
"""

__version__ = "0.1.0"

# Lazy imports to avoid dependency issues
def get_backend(provider: str, **kwargs):
    """Get an AI backend instance for the specified provider."""
    from lamina.backends import get_backend as _get_backend
    return _get_backend(provider, **kwargs)

def get_coordinator(**kwargs):
    """Get an AgentCoordinator instance."""
    from lamina.coordination import AgentCoordinator
    return AgentCoordinator(**kwargs)

def get_memory_store(**kwargs):
    """Get an AMemMemoryStore instance."""
    from lamina.memory import AMemMemoryStore
    return AMemMemoryStore(**kwargs)

__all__ = [
    "get_backend",
    "get_coordinator", 
    "get_memory_store",
    "__version__",
]