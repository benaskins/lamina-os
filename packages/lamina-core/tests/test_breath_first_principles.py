# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Unit Tests for breath-first principles integration.

These tests verify that Lamina Core API embodies breath-first development
principles in its structure and contracts.
"""

import time

import pytest

from lamina import get_coordinator


@pytest.mark.unit
class TestBreathFirstPrinciples:
    """Test integration of breath-first principles."""

    def test_natural_rhythm_embodiment(self):
        """Test that system embodies natural rhythm."""
        coordinator = get_coordinator()

        # Should have breathing capability
        assert hasattr(coordinator, "breath_modulation")
        assert hasattr(coordinator, "presence_pause")

        # Default should be breath-aware
        assert coordinator.breath_modulation is True
        assert coordinator.presence_pause > 0

    @pytest.mark.asyncio
    async def test_presence_over_speed(self):
        """Test prioritization of presence over speed."""
        agents = {
            "test_agent": {
                "name": "test_agent",
                "description": "Test agent for presence validation",
                "personality_traits": ["mindful"],
                "expertise_areas": ["testing"],
            }
        }

        # With presence-aware processing
        coordinator_present = get_coordinator(
            agents=agents, breath_modulation=True, presence_pause=0.1
        )

        # Without presence-aware processing
        coordinator_fast = get_coordinator(agents=agents, breath_modulation=False)

        # Measure processing times
        start_time = time.time()
        await coordinator_present.process_message("Test presence")
        present_time = time.time() - start_time

        start_time = time.time()
        await coordinator_fast.process_message("Test speed")
        fast_time = time.time() - start_time

        # Presence-aware should take longer (includes pause)
        assert present_time > fast_time
        assert present_time >= 0.1  # At least the mindful pause

    def test_wisdom_preservation(self):
        """Test that wisdom is preserved in architecture."""
        coordinator = get_coordinator()

        # Should have routing intelligence
        assert hasattr(coordinator, "intent_classifier")
        assert hasattr(coordinator, "_make_routing_decision")

        # Should have constraint systems
        assert hasattr(coordinator, "constraint_engine")
        assert hasattr(coordinator, "_apply_constraints")

        # Should track wisdom through statistics
        assert hasattr(coordinator, "routing_stats")
        assert hasattr(coordinator, "get_routing_stats")

    @pytest.mark.asyncio
    async def test_deliberate_consideration(self):
        """Test deliberate consideration over reactive responses."""
        agents = {
            "thoughtful": {
                "name": "thoughtful",
                "description": "Thoughtful deliberate agent",
                "personality_traits": ["thoughtful", "deliberate"],
                "expertise_areas": ["consideration"],
            }
        }

        coordinator = get_coordinator(agents=agents, presence_pause=0.05)

        # Should go through deliberate process
        start_time = time.time()
        response = await coordinator.process_message("Complex question requiring thought")
        processing_time = time.time() - start_time

        # Should include mindful pause for consideration
        assert processing_time >= 0.05
        assert response is not None
        assert len(response) > 0

    def test_sustainable_quality_focus(self):
        """Test focus on sustainable quality over rapid delivery."""
        coordinator = get_coordinator()

        # Should have quality measures built in
        assert hasattr(coordinator, "_apply_constraints")
        assert hasattr(coordinator, "constraint_engine")

        # Should track quality through routing decisions
        assert hasattr(coordinator, "_make_routing_decision")
        assert hasattr(coordinator, "_select_primary_agent")

        # Should support introspection for quality monitoring
        assert hasattr(coordinator, "get_agent_status")
        assert hasattr(coordinator, "get_routing_stats")

    @pytest.mark.asyncio
    async def test_mindful_processing_patterns(self):
        """Test mindful processing patterns in action."""
        agents = {
            "mindful_agent": {
                "name": "mindful_agent",
                "description": "Mindful processing specialist",
                "personality_traits": ["mindful", "present"],
                "expertise_areas": ["attunement"],
            }
        }

        coordinator = get_coordinator(agents=agents)

        # Process with mindful presence
        response = await coordinator.process_message("How do you stay present?")

        # Should route to appropriate agent
        assert "mindful_agent" in response

        # Should demonstrate understanding of mindfulness
        assert len(response) > 0

    def test_mindful_boundaries_maintenance(self):
        """Test maintenance of mindful boundaries."""
        coordinator = get_coordinator()

        # Should maintain appropriate presence attunement
        # (This is more about documentation and response patterns)
        assert hasattr(coordinator, "intent_classifier")

        # Should have proper constraint systems
        assert hasattr(coordinator, "constraint_engine")

        # Should maintain appropriate limitations
        stats = coordinator.get_routing_stats()
        assert isinstance(stats, dict)
        assert "total_requests" in stats

    def test_community_readiness_support(self):
        """Test support for community readiness principles."""
        coordinator = get_coordinator()

        # Should be introspectable for community understanding
        assert callable(getattr(coordinator, "list_available_agents", None))
        assert callable(getattr(coordinator, "get_agent_info", None))
        assert callable(getattr(coordinator, "get_agent_status", None))

        # Should provide clear information
        agents = coordinator.list_available_agents()
        assert isinstance(agents, list)

        status = coordinator.get_agent_status()
        assert isinstance(status, dict)
        assert "coordinator" in status

    def test_architectural_intention_alignment(self):
        """Test alignment between architectural intention and implementation."""
        # Test that what we built matches breath-first intentions
        coordinator = get_coordinator()

        # Intention: Natural rhythm → Implementation: breath_modulation
        assert hasattr(coordinator, "breath_modulation")

        # Intention: Deliberate pacing → Implementation: presence_pause
        assert hasattr(coordinator, "presence_pause")

        # Intention: Intelligent routing → Implementation: intent classification
        assert hasattr(coordinator, "intent_classifier")

        # Intention: Constraint attunement → Implementation: constraint engine
        assert hasattr(coordinator, "constraint_engine")

        # Intention: Wisdom preservation → Implementation: routing statistics
        assert hasattr(coordinator, "routing_stats")
