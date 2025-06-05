# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Base Agent class for Lamina OS

This module provides the foundational Agent class that all Lamina agents
inherit from. It implements breath-first principles, essence-based
configuration, and vow enforcement.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from lamina.agent_config import AgentConfig, load_agent_config
from lamina.coordination.constraint_engine import ConstraintEngine

logger = logging.getLogger(__name__)


@dataclass
class AgentEssence:
    """
    Represents an agent's essence layer configuration.

    The essence defines the core behavioral characteristics and constraints
    that shape how an agent operates within the Lamina framework.
    """

    # Core identity
    tag: str
    status: str
    core_tone: str

    # Behavioral characteristics
    behavioral_pillars: list[str] = field(default_factory=list)
    drift_boundaries: list[str] = field(default_factory=list)
    modulation_features: list[str] = field(default_factory=list)

    # Optional notes
    notes: Optional[str] = None

    # Additional metadata
    metadata: dict[str, Any] = field(default_factory=dict)


class Agent(ABC):
    """
    Base class for all Lamina agents.

    This class provides the foundational structure for creating presence-aware
    AI agents that operate according to breath-first principles and honor
    their defined essence and vows.
    """

    def __init__(
        self,
        name: str,
        config: Optional[AgentConfig] = None,
        essence: Optional[AgentEssence] = None,
        sanctuary_path: Optional[Path] = None,
    ):
        """
        Initialize an agent with configuration and essence.

        Args:
            name: The agent's identifier
            config: Optional explicit configuration (loads from sanctuary if not provided)
            essence: Optional essence configuration (loads from sanctuary if not provided)
            sanctuary_path: Optional path to sanctuary directory
        """
        self.name = name
        self.sanctuary_path = sanctuary_path or Path("sanctuary")

        # Load configuration
        self.config = config or load_agent_config(name)

        # Load essence
        self.essence = essence or self._load_essence()

        # Initialize constraint engine for vow enforcement
        self.constraint_engine = ConstraintEngine()

        # Initialize internal state
        self._breath_count = 0
        self._last_response = None
        self._context = {}

        logger.info(f"Initialized agent '{name}' with essence tag: {self.essence.tag}")

    def _load_essence(self) -> AgentEssence:
        """Load essence from markdown file in sanctuary."""
        essence_path = self.sanctuary_path / "essence" / f"essence.{self.name}.md"

        if not essence_path.exists():
            logger.warning(f"No essence file found for {self.name}, using defaults")
            return self._create_default_essence()

        try:
            from lamina.agents.essence_parser import EssenceParser

            parser = EssenceParser()
            return parser.parse_file(essence_path)
        except Exception as e:
            logger.error(f"Failed to load essence for {self.name}: {e}")
            return self._create_default_essence()

    def _create_default_essence(self) -> AgentEssence:
        """Create a default essence configuration."""
        return AgentEssence(
            tag=f"essence.{self.name}.default",
            status="uninitialized",
            core_tone="Present, attentive, breath-aware",
            behavioral_pillars=[
                "Breath-first operation",
                "Presence over performance",
                "Truth without harm",
            ],
            drift_boundaries=[
                "No reactive responses",
                "No performance of understanding",
                "No violation of established vows",
            ],
        )

    @abstractmethod
    async def process(self, message: str, context: Optional[dict] = None) -> str:
        """
        Process a message and generate a response.

        This method must be implemented by concrete agent classes to define
        their specific processing logic while honoring their essence.

        Args:
            message: The input message to process
            context: Optional context dictionary

        Returns:
            The agent's response
        """
        pass

    async def breathe(self) -> None:
        """
        Take a breath - a moment of conscious pause.

        This implements the breath-first principle by creating deliberate
        pauses in processing, preventing reactive responses.
        """
        self._breath_count += 1
        logger.debug(f"Agent {self.name} taking breath #{self._breath_count}")

        # Implement actual breath logic here
        # This could involve checking constraints, updating state, etc.
        await self._apply_breath_modulation()

    async def _apply_breath_modulation(self) -> None:
        """Apply breath-based modulation to agent state."""
        # This is where breath-based timing and pacing would be implemented
        # For now, it's a placeholder for the modulation logic
        pass

    def apply_constraints(self, content: str) -> str:
        """
        Apply vow-based constraints to content.

        Args:
            content: The content to constrain

        Returns:
            The constrained content
        """
        constraints = self._gather_active_constraints()
        result = self.constraint_engine.apply_constraints(content, constraints)

        if result.modified:
            logger.info(
                f"Applied constraints to {self.name}'s response: {result.applied_constraints}"
            )

        return result.content

    def _gather_active_constraints(self) -> list[str]:
        """Gather all active constraints from essence and vows."""
        constraints = []

        # Add drift boundaries as constraints
        constraints.extend(self.essence.drift_boundaries)

        # Add any additional constraints from config
        if hasattr(self.config, "constraints"):
            constraints.extend(self.config.constraints)

        return constraints

    def update_context(self, context: dict) -> None:
        """
        Update the agent's internal context.

        Args:
            context: New context information to merge
        """
        self._context.update(context)

    def get_state(self) -> dict:
        """
        Get the current state of the agent.

        Returns:
            Dictionary containing agent state information
        """
        return {
            "name": self.name,
            "essence_tag": self.essence.tag,
            "breath_count": self._breath_count,
            "config": {
                "ai_provider": self.config.ai_provider,
                "ai_model": self.config.ai_model,
            },
            "context": self._context,
        }

    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"Agent(name='{self.name}', essence='{self.essence.tag}')"

