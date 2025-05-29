# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Lamina Core - Breath-First AI Agent Framework

A framework for building AI agent systems with conscious, deliberate operations
that prioritize presence and wisdom over reactive speed.
"""

__version__ = "1.0.2"


# Lazy imports to avoid dependency issues
def get_backend(provider: str, config: dict = None):
    """Get an AI backend instance for the specified provider."""
    from lamina.backends import get_backend as _get_backend

    return _get_backend(provider, config or {})


def get_coordinator(agents: dict = None, **kwargs):
    """Get an AgentCoordinator instance."""
    from lamina.coordination.agent_coordinator import AgentCoordinator

    return AgentCoordinator(agents=agents or {}, **kwargs)


def get_memory_store(**kwargs):
    """Get a memory store instance."""
    from lamina.memory import AMemMemoryStore

    return AMemMemoryStore(**kwargs)


# Foundational classes for current capabilities
def create_simple_agent(name: str, config: dict):
    """Create a simple agent with current implementation."""
    from lamina.coordination.simple_agent import SimpleAgent

    return SimpleAgent(name, config)


__all__ = [
    "get_backend",
    "get_coordinator",
    "get_memory_store",
    "create_simple_agent",
    "__version__",
]
