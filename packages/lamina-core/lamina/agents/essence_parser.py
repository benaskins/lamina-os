# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Essence Parser for Lamina Agent Markdown Format

This module provides parsing functionality for agent essence definitions
written in the Lamina markdown format.
"""

import logging
import re
from pathlib import Path
from typing import Any, Optional

from lamina.agents.base import AgentEssence

logger = logging.getLogger(__name__)


class EssenceParser:
    """
    Parser for agent essence markdown files.

    Parses the structured markdown format used to define agent essences
    in the Lamina framework, extracting behavioral pillars, drift boundaries,
    and other core characteristics.
    """

    def parse_file(self, file_path: Path) -> AgentEssence:
        """
        Parse an essence file and return an AgentEssence object.

        Args:
            file_path: Path to the essence markdown file

        Returns:
            Parsed AgentEssence object

        Raises:
            ValueError: If the file format is invalid
        """
        if not file_path.exists():
            raise ValueError(f"Essence file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return self.parse_content(content)

    def parse_content(self, content: str) -> AgentEssence:
        """
        Parse essence content from a markdown string.

        Args:
            content: Markdown content to parse

        Returns:
            Parsed AgentEssence object
        """
        lines = content.strip().split("\n")

        # Extract metadata from header
        tag = self._extract_tag(lines)
        status = self._extract_status(lines)

        # Parse sections
        sections = self._parse_sections(lines)

        # Extract required fields
        core_tone = sections.get("Core Tone", "").strip()
        if not core_tone:
            raise ValueError("Missing required section: Core Tone")

        # Extract lists
        behavioral_pillars = self._parse_bullet_list(sections.get("Behavioral Pillars", ""))
        drift_boundaries = self._parse_bullet_list(sections.get("Drift Boundaries", ""))
        modulation_features = self._parse_bullet_list(sections.get("Modulation Features", ""))

        # Extract optional notes
        notes = sections.get("Notes", "").strip() if "Notes" in sections else None

        # Build metadata from any additional sections
        metadata = {}
        known_sections = {
            "Core Tone",
            "Behavioral Pillars",
            "Drift Boundaries",
            "Modulation Features",
            "Notes",
        }
        for section, content in sections.items():
            if section not in known_sections:
                metadata[section.lower().replace(" ", "_")] = content.strip()

        return AgentEssence(
            tag=tag,
            status=status,
            core_tone=core_tone,
            behavioral_pillars=behavioral_pillars,
            drift_boundaries=drift_boundaries,
            modulation_features=modulation_features,
            notes=notes,
            metadata=metadata,
        )

    def _extract_tag(self, lines: list[str]) -> str:
        """Extract tag from header."""
        for line in lines:
            match = re.match(r"\*\*Tag:\*\*\s*(.+)", line)
            if match:
                return match.group(1).strip()
        raise ValueError("Missing required field: Tag")

    def _extract_status(self, lines: list[str]) -> str:
        """Extract status from header."""
        for line in lines:
            match = re.match(r"\*\*Status:\*\*\s*(.+)", line)
            if match:
                return match.group(1).strip()
        return "undefined"  # Default if not specified

    def _parse_sections(self, lines: list[str]) -> dict[str, str]:
        """Parse markdown sections into a dictionary."""
        sections = {}
        current_section = None
        current_content = []

        for line in lines:
            # Check for section header (## Section Name)
            section_match = re.match(r"^##\s+(.+)", line)
            if section_match:
                # Save previous section
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()

                # Start new section
                current_section = section_match.group(1).strip()
                current_content = []
            elif current_section and line.strip():
                # Add content to current section
                current_content.append(line)

        # Save final section
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()

        return sections

    def _parse_bullet_list(self, content: str) -> list[str]:
        """Parse a bullet list from markdown content."""
        if not content:
            return []

        items = []
        lines = content.split("\n")
        current_item = []

        for line in lines:
            # Check for bullet point
            bullet_match = re.match(r"^[-*]\s+(.+)", line)
            if bullet_match:
                # Save previous item
                if current_item:
                    items.append(" ".join(current_item))

                # Extract main content and key if present
                item_content = bullet_match.group(1)

                # Handle bold keys (e.g., **Key:** Value)
                key_match = re.match(r"\*\*([^:]+):\*\*\s*(.+)", item_content)
                if key_match:
                    items.append(f"{key_match.group(1)}: {key_match.group(2)}")
                else:
                    current_item = [item_content]
            elif line.strip() and current_item:
                # Continuation of previous item
                current_item.append(line.strip())

        # Save final item
        if current_item:
            items.append(" ".join(current_item))

        return items

    def validate_essence(self, essence: AgentEssence) -> list[str]:
        """
        Validate an essence configuration.

        Args:
            essence: The essence to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        if not essence.tag:
            errors.append("Missing required field: tag")

        if not essence.core_tone:
            errors.append("Missing required field: core_tone")

        if not essence.behavioral_pillars:
            errors.append("Behavioral pillars should not be empty")

        if not essence.drift_boundaries:
            errors.append("Drift boundaries should not be empty")

        return errors

