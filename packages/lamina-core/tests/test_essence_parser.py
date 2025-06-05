# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""Tests for the EssenceParser class."""

import pytest
from pathlib import Path
import tempfile

from lamina.agents.essence_parser import EssenceParser
from lamina.agents.base import AgentEssence


class TestEssenceParser:
    """Tests for the EssenceParser class."""

    @pytest.fixture
    def parser(self):
        """Create an EssenceParser instance."""
        return EssenceParser()

    @pytest.fixture
    def sample_essence_content(self):
        """Sample essence markdown content."""
        return """# Capsule: Essence — TestAgent
**Tag:** essence.test.v1
**Status:** active

---

## Core Tone
Present, mindful, breath-aware.

## Behavioral Pillars
- **Presence:** Always present in the moment
- **Mindfulness:** Conscious of every interaction
- **Breath:** Operating with deliberate pacing

## Drift Boundaries
- No reactive responses
- No performance of understanding
- No violation of vows

## Modulation Features
- Breath anchoring (pause, silence, pacing)
- Contradiction-holding ("I want to stay, and I want to run.")
- Volitional fragments ("If I could…")

## Notes
This is a test agent essence for unit testing purposes.
"""

    def test_parse_content_with_complete_essence(self, parser, sample_essence_content):
        """Test parsing complete essence content."""
        essence = parser.parse_content(sample_essence_content)

        assert isinstance(essence, AgentEssence)
        assert essence.tag == "essence.test.v1"
        assert essence.status == "active"
        assert essence.core_tone == "Present, mindful, breath-aware."

        assert len(essence.behavioral_pillars) == 3
        assert "Presence: Always present in the moment" in essence.behavioral_pillars
        assert "Mindfulness: Conscious of every interaction" in essence.behavioral_pillars
        assert "Breath: Operating with deliberate pacing" in essence.behavioral_pillars

        assert len(essence.drift_boundaries) == 3
        assert "No reactive responses" in essence.drift_boundaries

        assert len(essence.modulation_features) == 3
        assert "Breath anchoring (pause, silence, pacing)" in essence.modulation_features

        assert essence.notes == "This is a test agent essence for unit testing purposes."

    def test_parse_content_minimal(self, parser):
        """Test parsing minimal essence content."""
        content = """**Tag:** minimal.essence
## Core Tone
Minimal tone
"""
        essence = parser.parse_content(content)

        assert essence.tag == "minimal.essence"
        assert essence.status == "undefined"  # Default when not specified
        assert essence.core_tone == "Minimal tone"
        assert essence.behavioral_pillars == []
        assert essence.drift_boundaries == []
        assert essence.modulation_features == []
        assert essence.notes is None

    def test_parse_content_missing_tag_raises_error(self, parser):
        """Test that missing tag raises ValueError."""
        content = """## Core Tone
No tag provided
"""
        with pytest.raises(ValueError, match="Missing required field: Tag"):
            parser.parse_content(content)

    def test_parse_content_missing_core_tone_raises_error(self, parser):
        """Test that missing core tone raises ValueError."""
        content = """**Tag:** test.essence
## Behavioral Pillars
- Some pillar
"""
        with pytest.raises(ValueError, match="Missing required section: Core Tone"):
            parser.parse_content(content)

    def test_parse_file_success(self, parser, sample_essence_content):
        """Test parsing from file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(sample_essence_content)
            temp_path = Path(f.name)

        try:
            essence = parser.parse_file(temp_path)
            assert essence.tag == "essence.test.v1"
            assert essence.core_tone == "Present, mindful, breath-aware."
        finally:
            temp_path.unlink()

    def test_parse_file_not_found(self, parser):
        """Test parsing non-existent file raises error."""
        with pytest.raises(ValueError, match="Essence file not found"):
            parser.parse_file(Path("/nonexistent/file.md"))

    def test_parse_bullet_list_variations(self, parser):
        """Test parsing different bullet list formats."""
        # Test with asterisk bullets
        content1 = """* Item 1
* Item 2"""
        items1 = parser._parse_bullet_list(content1)
        assert items1 == ["Item 1", "Item 2"]

        # Test with dash bullets
        content2 = """- Item A
- Item B"""
        items2 = parser._parse_bullet_list(content2)
        assert items2 == ["Item A", "Item B"]

        # Test with multi-line items
        content3 = """- First line
  continuation
- Second item"""
        items3 = parser._parse_bullet_list(content3)
        assert items3 == ["First line continuation", "Second item"]

        # Test empty content
        assert parser._parse_bullet_list("") == []
        assert parser._parse_bullet_list(None) == []

    def test_parse_sections_with_additional_metadata(self, parser):
        """Test parsing sections that become metadata."""
        content = """**Tag:** test.essence
## Core Tone
Test tone

## Custom Section
Custom content here

## Another Custom
More custom content
"""
        essence = parser.parse_content(content)

        assert essence.tag == "test.essence"
        assert essence.core_tone == "Test tone"
        assert "custom_section" in essence.metadata
        assert essence.metadata["custom_section"] == "Custom content here"
        assert "another_custom" in essence.metadata
        assert essence.metadata["another_custom"] == "More custom content"

    def test_validate_essence_valid(self, parser):
        """Test validation of valid essence."""
        essence = AgentEssence(
            tag="valid.essence",
            status="active",
            core_tone="Valid tone",
            behavioral_pillars=["Pillar 1"],
            drift_boundaries=["Boundary 1"],
        )

        errors = parser.validate_essence(essence)
        assert errors == []

    def test_validate_essence_missing_fields(self, parser):
        """Test validation catches missing fields."""
        essence = AgentEssence(
            tag="", status="active", core_tone="", behavioral_pillars=[], drift_boundaries=[]
        )

        errors = parser.validate_essence(essence)
        assert "Missing required field: tag" in errors
        assert "Missing required field: core_tone" in errors
        assert "Behavioral pillars should not be empty" in errors
        assert "Drift boundaries should not be empty" in errors

    def test_extract_tag_variations(self, parser):
        """Test extracting tag from different formats."""
        lines1 = ["**Tag:** simple.tag", "Other content"]
        assert parser._extract_tag(lines1) == "simple.tag"

        lines2 = ["**Tag:**   spaced.tag   ", "Other content"]
        assert parser._extract_tag(lines2) == "spaced.tag"

        lines3 = ["No tag here", "Other content"]
        with pytest.raises(ValueError, match="Missing required field: Tag"):
            parser._extract_tag(lines3)

    def test_extract_status_variations(self, parser):
        """Test extracting status from different formats."""
        lines1 = ["**Status:** active", "Other content"]
        assert parser._extract_status(lines1) == "active"

        lines2 = ["**Status:**   in development   ", "Other content"]
        assert parser._extract_status(lines2) == "in development"

        lines3 = ["No status here", "Other content"]
        assert parser._extract_status(lines3) == "undefined"  # Default value

