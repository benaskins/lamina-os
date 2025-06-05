# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Lamina Core - Breath-First AI Agent Framework

A framework for building AI agent systems with mindful, deliberate operations
that prioritize presence and wisdom over reactive speed.
"""

# Import core classes first
from lamina.agent_config import AgentConfig, load_agent_config
from lamina.agents import Agent, AgentEssence, EssenceParser
from lamina.coordination import AgentCoordinator, ConstraintEngine
from lamina.llm_base import LLMClient
from lamina.llm_base import get_llm_client as _get_llm_client

__version__ = "0.2.1"


# Lazy imports to avoid dependency issues
def get_llm_client(config: dict = None):
    """Get an LLM client instance for connecting to lamina-llm-serve."""
    from lamina.llm_client import LaminaLLMClient

    return LaminaLLMClient(config or {})


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


# Memory store is optional - requires chromadb
try:
    from lamina.memory import AMEMMemoryStore
except ImportError:
    AMEMMemoryStore = None

__all__ = [
    # Agent classes
    "Agent",
    "AgentConfig",
    "AgentEssence",
    "EssenceParser",
    "load_agent_config",
    # Coordination
    "AgentCoordinator",
    "ConstraintEngine",
    # LLM clients
    "LLMClient",
    # Memory
    "AMEMMemoryStore",
    # Factory functions
    "get_llm_client",
    "get_coordinator",
    "get_memory_store",
    "create_simple_agent",
    # Version
    "__version__",
]
