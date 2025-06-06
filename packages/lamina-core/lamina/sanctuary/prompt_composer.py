# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Dynamic Prompt Composer for Lamina Sanctuary System

This module implements the vision of dynamic prompt composition where
agent essences, room contexts, and modulation rules are composed at
runtime from markdown-based sanctuary components.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from lamina.agents.essence_parser import EssenceParser

logger = logging.getLogger(__name__)


@dataclass
class Room:
    """Represents a contextual space that modulates agent behavior."""

    name: str
    purpose: str
    atmosphere: dict[str, str]
    modulation: dict[str, str]
    constraints: list[str]
    metadata: dict[str, Any]


@dataclass
class ModulationRule:
    """Represents a rule that modulates agent behavior."""

    name: str
    trigger: str  # When this rule applies
    effect: str  # How it modulates behavior
    priority: int
    metadata: dict[str, Any]


class RoomParser:
    """Parser for room markdown files."""

    def parse_file(self, file_path: Path) -> Room:
        """Parse a room definition from markdown."""
        if not file_path.exists():
            raise ValueError(f"Room file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        return self.parse_content(content)

    def parse_content(self, content: str) -> Room:
        """Parse room content from markdown."""
        lines = content.strip().split("\n")
        sections = self._parse_sections(lines)

        # Extract required fields
        name = self._extract_name(lines)
        purpose = sections.get("Purpose", "").strip()

        if not purpose:
            raise ValueError("Missing required section: Purpose")

        # Parse atmosphere as key-value pairs
        atmosphere = self._parse_key_value_section(sections.get("Atmosphere", ""))

        # Parse modulation settings
        modulation = self._parse_key_value_section(sections.get("Modulation", ""))

        # Parse constraints as bullet list
        constraints = self._parse_bullet_list(sections.get("Constraints", ""))

        # Build metadata from additional sections
        metadata = {}
        known_sections = {"Purpose", "Atmosphere", "Modulation", "Constraints"}
        for section, section_content in sections.items():
            if section not in known_sections:
                metadata[section.lower().replace(" ", "_")] = section_content.strip()

        return Room(
            name=name,
            purpose=purpose,
            atmosphere=atmosphere,
            modulation=modulation,
            constraints=constraints,
            metadata=metadata,
        )

    def _extract_name(self, lines: list[str]) -> str:
        """Extract room name from header."""
        for line in lines:
            if line.startswith("# Room:"):
                return line.replace("# Room:", "").strip()
        raise ValueError("Missing room name in header")

    def _parse_sections(self, lines: list[str]) -> dict[str, str]:
        """Parse markdown sections."""
        sections = {}
        current_section = None
        current_content = []

        for line in lines:
            if line.startswith("## "):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            elif current_section and line.strip():
                current_content.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _parse_key_value_section(self, content: str) -> dict[str, str]:
        """Parse a section with key: value pairs."""
        result = {}
        if not content:
            return result

        for line in content.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip("- *")
                result[key.strip()] = value.strip()

        return result

    def _parse_bullet_list(self, content: str) -> list[str]:
        """Parse bullet list from content."""
        if not content:
            return []

        items = []
        for line in content.split("\n"):
            if line.strip().startswith(("-", "*")):
                items.append(line.strip()[1:].strip())

        return items


class ModulationParser:
    """Parser for modulation rule markdown files."""

    def parse_file(self, file_path: Path) -> list[ModulationRule]:
        """Parse modulation rules from markdown."""
        if not file_path.exists():
            raise ValueError(f"Modulation file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        return self.parse_content(content)

    def parse_content(self, content: str) -> list[ModulationRule]:
        """Parse modulation rules from markdown content."""
        lines = content.strip().split("\n")
        sections = self._parse_sections(lines)

        rules = []
        for section_name, section_content in sections.items():
            if section_name.startswith("Rule:"):
                rule_name = section_name.replace("Rule:", "").strip()
                rule = self._parse_rule(rule_name, section_content)
                rules.append(rule)

        return rules

    def _parse_rule(self, name: str, content: str) -> ModulationRule:
        """Parse a single modulation rule."""
        lines = content.split("\n")
        trigger = ""
        effect = ""
        priority = 50  # Default priority
        metadata = {}

        for line in lines:
            if line.startswith("Trigger:"):
                trigger = line.replace("Trigger:", "").strip()
            elif line.startswith("Effect:"):
                effect = line.replace("Effect:", "").strip()
            elif line.startswith("Priority:"):
                try:
                    priority = int(line.replace("Priority:", "").strip())
                except ValueError:
                    priority = 50
            elif ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip().lower()] = value.strip()

        return ModulationRule(
            name=name, trigger=trigger, effect=effect, priority=priority, metadata=metadata
        )

    def _parse_sections(self, lines: list[str]) -> dict[str, str]:
        """Parse markdown sections."""
        sections = {}
        current_section = None
        current_content = []

        for line in lines:
            if line.startswith("## "):
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = line[3:].strip()
                current_content = []
            elif current_section:
                current_content.append(line)

        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections


class PromptComposer:
    """
    Dynamic prompt composer that assembles prompts from sanctuary components.

    This class implements the vision of runtime prompt composition where
    agent essences, room contexts, and modulation rules are combined
    dynamically on each conversation turn.
    """

    def __init__(self, sanctuary_path: Path):
        """Initialize the prompt composer with a sanctuary path."""
        self.sanctuary_path = sanctuary_path
        self.essence_parser = EssenceParser()
        self.room_parser = RoomParser()
        self.modulation_parser = ModulationParser()

        # Cache for parsed components
        self._essence_cache = {}
        self._room_cache = {}
        self._modulation_cache = {}

    def compose_prompt(
        self,
        agent_name: str,
        room_name: str,
        message: str,
        context: dict[str, Any] | None = None,
        active_modulations: list[str] | None = None,
    ) -> str:
        """
        Compose a complete prompt from sanctuary components.

        Args:
            agent_name: Name of the agent
            room_name: Name of the current room
            message: User's message
            context: Additional context
            active_modulations: List of active modulation rule names

        Returns:
            Composed prompt string
        """
        # Load agent essence
        essence = self._load_agent_essence(agent_name)

        # Load room definition
        room = self._load_room(room_name)

        # Load and apply modulation rules
        modulations = []
        if active_modulations:
            for mod_name in active_modulations:
                rules = self._load_modulation_rules(mod_name)
                modulations.extend(rules)

        # Sort modulations by priority
        modulations.sort(key=lambda r: r.priority, reverse=True)

        # Compose the prompt
        prompt_parts = []

        # 1. Base agent identity from essence
        prompt_parts.append(self._compose_essence_section(agent_name, essence))

        # 2. Room context and atmosphere
        prompt_parts.append(self._compose_room_section(room))

        # 3. Active modulation effects
        if modulations:
            prompt_parts.append(self._compose_modulation_section(modulations))

        # 4. Constraints from both essence and room
        all_constraints = essence.drift_boundaries + room.constraints
        if all_constraints:
            prompt_parts.append(self._compose_constraints_section(all_constraints))

        # 5. Context if provided
        if context:
            prompt_parts.append(self._compose_context_section(context))

        # 6. User message
        prompt_parts.append(f"\nUser: {message}\n\nResponse:")

        return "\n\n".join(prompt_parts)

    def compose_baseline_prompt(
        self, agent_name: str, message: str, context: dict[str, Any] | None = None
    ) -> str:
        """
        Compose a baseline prompt using only agent essence (no room modulation).

        This simulates the old hardcoded prompt approach for comparison.

        Args:
            agent_name: Name of the agent
            message: User's message
            context: Additional context

        Returns:
            Baseline prompt string without room modulation
        """
        # Load agent essence only
        essence = self._load_agent_essence(agent_name)

        # Compose simplified prompt similar to old hardcoded approach
        prompt_parts = []

        # Basic agent identity
        prompt_parts.append(self._compose_essence_section(agent_name, essence))

        # Basic constraints only from essence
        if essence.drift_boundaries:
            prompt_parts.append(self._compose_constraints_section(essence.drift_boundaries))

        # Context if provided
        if context:
            prompt_parts.append(self._compose_context_section(context))

        # User message
        prompt_parts.append(f"\nUser: {message}\n\nResponse:")

        return "\n\n".join(prompt_parts)

    def _load_agent_essence(self, agent_name: str):
        """Load and cache agent essence."""
        if agent_name not in self._essence_cache:
            essence_path = self.sanctuary_path / "agents" / f"{agent_name}.md"
            self._essence_cache[agent_name] = self.essence_parser.parse_file(essence_path)
        return self._essence_cache[agent_name]

    def _load_room(self, room_name: str) -> Room:
        """Load and cache room definition."""
        if room_name not in self._room_cache:
            room_path = self.sanctuary_path / "rooms" / f"{room_name}.md"
            self._room_cache[room_name] = self.room_parser.parse_file(room_path)
        return self._room_cache[room_name]

    def _load_modulation_rules(self, modulation_name: str) -> list[ModulationRule]:
        """Load and cache modulation rules."""
        if modulation_name not in self._modulation_cache:
            mod_path = self.sanctuary_path / "modulation" / f"{modulation_name}.md"
            self._modulation_cache[modulation_name] = self.modulation_parser.parse_file(mod_path)
        return self._modulation_cache[modulation_name]

    def _compose_essence_section(self, agent_name: str, essence) -> str:
        """Compose the agent essence section of the prompt."""
        parts = [f"You are {agent_name}, an agent with the following essence:"]

        parts.append(f"\nCore Tone: {essence.core_tone}")

        if essence.behavioral_pillars:
            parts.append("\nBehavioral Pillars:")
            for pillar in essence.behavioral_pillars:
                parts.append(f"- {pillar}")

        if essence.modulation_features:
            parts.append("\nYour modulation features include:")
            for feature in essence.modulation_features:
                parts.append(f"- {feature}")

        if essence.notes:
            parts.append(f"\nAdditional notes: {essence.notes}")

        return "\n".join(parts)

    def _compose_room_section(self, room: Room) -> str:
        """Compose the room context section."""
        parts = [f"You are currently in the {room.name}, a space for {room.purpose}."]

        if room.atmosphere:
            parts.append("\nThe atmosphere here is:")
            for key, value in room.atmosphere.items():
                parts.append(f"- {key}: {value}")

        if room.modulation:
            parts.append("\nIn this room, modulate your responses with:")
            for key, value in room.modulation.items():
                parts.append(f"- {key}: {value}")

        return "\n".join(parts)

    def _compose_modulation_section(self, modulations: list[ModulationRule]) -> str:
        """Compose the active modulation section."""
        parts = ["Active modulation rules:"]

        for rule in modulations:
            parts.append(f"\n- {rule.name}: {rule.effect}")

        return "\n".join(parts)

    def _compose_constraints_section(self, constraints: list[str]) -> str:
        """Compose the constraints section."""
        parts = ["You must honor these boundaries and constraints:"]

        for constraint in constraints:
            parts.append(f"- {constraint}")

        return "\n".join(parts)

    def _compose_context_section(self, context: dict[str, Any]) -> str:
        """Compose the context section."""
        parts = ["Context:"]

        for key, value in context.items():
            parts.append(f"- {key}: {value}")

        return "\n".join(parts)
