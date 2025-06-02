# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Unit Tests for AgentCoordinator - the heart of breath-first coordination.

These tests validate coordinator API contracts and mock behavior.
For real AI coordination testing, see test_real_agent_coordination.py.
"""

import time

import pytest

from lamina import get_coordinator


@pytest.mark.unit
class TestAgentCoordinator:
    """Test breath-first agent coordination."""

    def setup_method(self):
        """Setup test agents for each test."""
        self.test_agents = {
            "assistant": {
                "name": "assistant",
                "description": "Helpful general purpose assistant",
                "personality_traits": ["helpful", "patient"],
                "expertise_areas": ["general", "conversation"],
            },
            "researcher": {
                "name": "researcher",
                "description": "Analytical research specialist",
                "personality_traits": ["analytical", "thorough"],
                "expertise_areas": ["research", "analysis"],
            },
            "creative": {
                "name": "creative",
                "description": "Creative and artistic agent",
                "personality_traits": ["creative", "imaginative"],
                "expertise_areas": ["writing", "art", "storytelling"],
            },
        }

    def test_coordinator_creation(self):
        """Test basic coordinator creation."""
        coordinator = get_coordinator(agents=self.test_agents)
        assert coordinator is not None
        assert len(coordinator.agents) == 3
        assert coordinator.breath_modulation is True
        assert coordinator.presence_pause == 0.5

    def test_breath_modulation_settings(self):
        """Test breath modulation configuration."""
        # Test with custom settings
        coordinator = get_coordinator(
            agents=self.test_agents, breath_modulation=False, presence_pause=1.0
        )
        assert coordinator.breath_modulation is False
        assert coordinator.presence_pause == 1.0

    @pytest.mark.asyncio
    async def test_presence_aware_processing(self):
        """Test that presence-aware pauses actually happen."""
        coordinator = get_coordinator(
            agents=self.test_agents,
            breath_modulation=True,
            presence_pause=0.2,  # Short pause for testing
        )

        start_time = time.time()
        response = await coordinator.process_message("Hello, how are you?")
        end_time = time.time()

        # Should take at least the mindful pause time
        assert (end_time - start_time) >= 0.2
        assert response is not None
        assert len(response) > 0

    @pytest.mark.asyncio
    async def test_agent_routing_general(self):
        """Test routing to general assistant."""
        coordinator = get_coordinator(agents=self.test_agents)

        response = await coordinator.process_message("What's 2+2?")
        assert "assistant" in response.lower()
        assert "helpful" in response or "happy to help" in response

    @pytest.mark.asyncio
    async def test_agent_routing_research(self):
        """Test routing to research specialist."""
        coordinator = get_coordinator(agents=self.test_agents)

        response = await coordinator.process_message("Can you research quantum computing?")
        assert "researcher" in response.lower()
        assert "analyze" in response.lower()

    @pytest.mark.asyncio
    async def test_agent_routing_creative(self):
        """Test routing to creative agent."""
        coordinator = get_coordinator(agents=self.test_agents)

        response = await coordinator.process_message("Write me a creative story about time travel")
        assert "creative" in response.lower()
        assert "exciting creative challenge" in response.lower()

    def test_agent_status_introspection(self):
        """Test agent status and introspection capabilities."""
        coordinator = get_coordinator(agents=self.test_agents)

        # Test agent listing
        agents = coordinator.list_available_agents()
        assert len(agents) == 3
        assert "assistant" in agents
        assert "researcher" in agents
        assert "creative" in agents

        # Test agent info
        agent_info = coordinator.get_agent_info("creative")
        assert agent_info is not None
        assert agent_info["name"] == "creative"
        assert "writing" in agent_info["capabilities"]

        # Test agent status
        status = coordinator.get_agent_status()
        assert status["coordinator"]["agents_count"] == 3
        assert status["coordinator"]["breath_modulation"] is True
        assert "creative" in status["agents"]

    @pytest.mark.asyncio
    async def test_routing_statistics(self):
        """Test routing statistics tracking."""
        coordinator = get_coordinator(agents=self.test_agents)

        # Process several messages
        await coordinator.process_message("Hello")  # assistant
        await coordinator.process_message("Research AI")  # researcher
        await coordinator.process_message("Write a poem")  # creative

        stats = coordinator.get_routing_stats()
        assert stats["total_requests"] == 3
        assert len(stats["routing_decisions"]) > 0

    @pytest.mark.asyncio
    async def test_fallback_behavior(self):
        """Test fallback when requested agent doesn't exist."""
        # Create coordinator with only one agent
        single_agent = {"assistant": self.test_agents["assistant"]}
        coordinator = get_coordinator(agents=single_agent)

        # Request should still work, falling back to available agent
        response = await coordinator.process_message("Research quantum physics")
        assert response is not None
        assert len(response) > 0

    def test_breath_first_principles_embodiment(self):
        """Test that coordinator embodies breath-first principles."""
        coordinator = get_coordinator(agents=self.test_agents)

        # Should have presence-aware settings
        assert hasattr(coordinator, "breath_modulation")
        assert hasattr(coordinator, "presence_pause")

        # Should use MockIntentClassifier (supports creative routing)
        assert hasattr(coordinator, "intent_classifier")
        assert coordinator.intent_classifier is not None

        # Should have constraint engine
        assert hasattr(coordinator, "constraint_engine")
        assert coordinator.constraint_engine is not None

    @pytest.mark.asyncio
    async def test_no_breathing_performance_mode(self):
        """Test performance mode with no breathing pauses."""
        coordinator = get_coordinator(agents=self.test_agents, breath_modulation=False)

        start_time = time.time()
        response = await coordinator.process_message("Quick test")
        end_time = time.time()

        # Should be much faster without breathing (but allow for mock processing time)
        assert (end_time - start_time) < 0.5
        assert response is not None

    @pytest.mark.asyncio
    async def test_secondary_agent_enhancement(self):
        """Test that secondary agents are properly awaited and applied."""
        agents = dict(self.test_agents)
        coordinator = get_coordinator(agents=agents)

        primary = await coordinator._route_to_agent("assistant", "test", None)
        enhanced = await coordinator._apply_secondary_agents(primary, ["researcher"], "test", None)

        assert "Additional analysis:" in enhanced.content
