# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""Tests for the base Agent class."""

from unittest.mock import Mock, patch

import pytest

from lamina.agent_config import AgentConfig
from lamina.agents.base import Agent, AgentEssence


class ConcreteAgent(Agent):
    """Concrete implementation of Agent for testing."""

    async def process(self, message: str, context=None):
        """Simple process implementation for testing."""
        await self.breathe()
        response = f"Processed: {message}"
        return self.apply_constraints(response)


class TestAgentBase:
    """Tests for the base Agent class."""

    def test_agent_initialization_with_defaults(self):
        """Test agent initialization with default values."""
        agent = ConcreteAgent("test_agent")

        assert agent.name == "test_agent"
        assert isinstance(agent.config, AgentConfig)
        assert isinstance(agent.essence, AgentEssence)
        assert agent.essence.tag == "essence.test_agent.default"
        assert agent._breath_count == 0

    def test_agent_initialization_with_config(self):
        """Test agent initialization with explicit config."""
        config = AgentConfig(
            name="test_agent",
            description="Test agent",
            ai_provider="test_provider",
            ai_model="test_model",
        )

        agent = ConcreteAgent("test_agent", config=config)

        assert agent.config == config
        assert agent.config.ai_provider == "test_provider"

    def test_agent_initialization_with_essence(self):
        """Test agent initialization with explicit essence."""
        essence = AgentEssence(
            tag="test.essence.v1",
            status="active",
            core_tone="Test tone",
            behavioral_pillars=["Test pillar 1", "Test pillar 2"],
            drift_boundaries=["No test drift"],
        )

        agent = ConcreteAgent("test_agent", essence=essence)

        assert agent.essence == essence
        assert agent.essence.behavioral_pillars == ["Test pillar 1", "Test pillar 2"]

    @pytest.mark.asyncio
    async def test_breathe_increments_counter(self):
        """Test that breathe() increments the breath counter."""
        agent = ConcreteAgent("test_agent")

        assert agent._breath_count == 0

        await agent.breathe()
        assert agent._breath_count == 1

        await agent.breathe()
        assert agent._breath_count == 2

    def test_apply_constraints_with_no_modifications(self):
        """Test apply_constraints when no modifications are needed."""
        agent = ConcreteAgent("test_agent")

        # Mock the constraint engine
        mock_result = Mock()
        mock_result.modified = False
        mock_result.content = "Original content"

        with patch.object(agent.constraint_engine, "apply_constraints", return_value=mock_result):
            result = agent.apply_constraints("Original content")

            assert result == "Original content"

    def test_apply_constraints_with_modifications(self):
        """Test apply_constraints when modifications are applied."""
        agent = ConcreteAgent("test_agent")

        # Mock the constraint engine
        mock_result = Mock()
        mock_result.modified = True
        mock_result.content = "Modified content"
        mock_result.applied_constraints = ["constraint1", "constraint2"]

        with patch.object(agent.constraint_engine, "apply_constraints", return_value=mock_result):
            result = agent.apply_constraints("Original content")

            assert result == "Modified content"

    def test_gather_active_constraints(self):
        """Test gathering constraints from essence and config."""
        essence = AgentEssence(
            tag="test.essence",
            status="active",
            core_tone="Test",
            drift_boundaries=["boundary1", "boundary2"],
        )

        agent = ConcreteAgent("test_agent", essence=essence)

        constraints = agent._gather_active_constraints()

        assert "boundary1" in constraints
        assert "boundary2" in constraints

    def test_update_context(self):
        """Test updating agent context."""
        agent = ConcreteAgent("test_agent")

        assert agent._context == {}

        agent.update_context({"key1": "value1"})
        assert agent._context == {"key1": "value1"}

        agent.update_context({"key2": "value2"})
        assert agent._context == {"key1": "value1", "key2": "value2"}

        # Test overwriting
        agent.update_context({"key1": "new_value"})
        assert agent._context == {"key1": "new_value", "key2": "value2"}

    def test_get_state(self):
        """Test getting agent state."""
        config = AgentConfig(name="test_agent", ai_provider="test_provider", ai_model="test_model")
        essence = AgentEssence(tag="test.essence.v1", status="active", core_tone="Test")

        agent = ConcreteAgent("test_agent", config=config, essence=essence)
        agent.update_context({"test_key": "test_value"})

        state = agent.get_state()

        assert state["name"] == "test_agent"
        assert state["essence_tag"] == "test.essence.v1"
        assert state["breath_count"] == 0
        assert state["config"]["ai_provider"] == "test_provider"
        assert state["config"]["ai_model"] == "test_model"
        assert state["context"] == {"test_key": "test_value"}

    @pytest.mark.asyncio
    async def test_process_implementation(self):
        """Test the concrete process implementation."""
        agent = ConcreteAgent("test_agent")

        # Mock apply_constraints to return the input
        with patch.object(agent, "apply_constraints", side_effect=lambda x: x):
            result = await agent.process("Hello")

            assert result == "Processed: Hello"
            assert agent._breath_count == 1  # Should have taken a breath

    def test_repr(self):
        """Test string representation of agent."""
        essence = AgentEssence(tag="test.essence.v1", status="active", core_tone="Test")
        agent = ConcreteAgent("test_agent", essence=essence)

        assert repr(agent) == "Agent(name='test_agent', essence='test.essence.v1')"

    @patch("lamina.agents.base.Path.exists")
    @patch("lamina.agents.essence_parser.EssenceParser")
    def test_load_essence_from_file(self, mock_parser_class, mock_exists):
        """Test loading essence from markdown file."""
        mock_exists.return_value = True

        mock_essence = AgentEssence(tag="loaded.essence", status="active", core_tone="Loaded tone")

        mock_parser = Mock()
        mock_parser.parse_file.return_value = mock_essence
        mock_parser_class.return_value = mock_parser

        agent = ConcreteAgent("test_agent")

        assert agent.essence == mock_essence
        mock_parser.parse_file.assert_called_once()

    def test_create_default_essence(self):
        """Test creation of default essence."""
        agent = ConcreteAgent("test_agent")
        essence = agent._create_default_essence()

        assert essence.tag == "essence.test_agent.default"
        assert essence.status == "uninitialized"
        assert essence.core_tone == "Present, attentive, breath-aware"
        assert len(essence.behavioral_pillars) == 3
        assert len(essence.drift_boundaries) == 3
