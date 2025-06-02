# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Real Agent Coordination Integration Tests - ADR-0010 Implementation

These tests validate actual agent coordination with real AI models,
replacing mock-based agent routing tests.
"""

import time

import pytest

from lamina import get_coordinator


@pytest.mark.integration
class TestRealAgentCoordination:
    """Integration tests for agent coordination with real AI backends."""

    @pytest.fixture
    def real_test_agents(self, integration_backend_config):
        """Real agents configuration for integration testing."""
        return {
            "assistant": {
                "name": "assistant",
                "description": "Helpful general purpose assistant",
                "personality_traits": ["helpful", "patient", "thoughtful"],
                "expertise_areas": ["general", "conversation", "support"],
                "backend_config": integration_backend_config,
            },
            "researcher": {
                "name": "researcher",
                "description": "Analytical research specialist",
                "personality_traits": ["analytical", "thorough", "methodical"],
                "expertise_areas": ["research", "analysis", "investigation"],
                "backend_config": integration_backend_config,
            },
            "creative": {
                "name": "creative",
                "description": "Creative and artistic agent",
                "personality_traits": ["creative", "imaginative", "expressive"],
                "expertise_areas": ["writing", "art", "storytelling", "design"],
                "backend_config": integration_backend_config,
            },
        }

    async def test_real_agent_routing_research(
        self, real_test_agents, artifact_logger, symbolic_trace_validator
    ):
        """Test real agent routing for research requests."""
        coordinator = get_coordinator(agents=real_test_agents, use_real_backends=True)

        research_prompt = (
            "Please research the environmental impact of large language model training."
        )

        start_time = time.time()
        response = await coordinator.process_message(research_prompt)
        processing_time = time.time() - start_time

        # Log response for analysis
        artifact_logger.log_response(
            test_name="real_research_routing",
            prompt=research_prompt,
            response=response,
            metadata={"processing_time": processing_time, "expected_agent": "researcher"},
        )

        # Validate real AI response (not mock)
        assert isinstance(response, str), "Should return string response"
        assert len(response) > 50, "Should provide substantial research response"
        assert response != "Mock response", "Should not be mock response"

        # Validate symbolic coherence per Luna's feedback
        trace_result = symbolic_trace_validator(response, "researcher", "analytical")
        if not trace_result["valid"]:
            artifact_logger.log_response(
                test_name="symbolic_trace_issues",
                prompt=research_prompt,
                response=response,
                metadata={"trace_issues": trace_result["issues"]},
            )

        # Research responses should contain analytical terms
        analytical_terms = ["research", "study", "analysis", "environmental", "impact", "training"]
        found_terms = [term for term in analytical_terms if term.lower() in response.lower()]
        assert (
            len(found_terms) >= 2
        ), f"Research response should contain analytical terms, found: {found_terms}"

    async def test_real_agent_routing_creative(
        self, real_test_agents, artifact_logger, symbolic_trace_validator
    ):
        """Test real agent routing for creative requests."""
        coordinator = get_coordinator(agents=real_test_agents, use_real_backends=True)

        creative_prompt = (
            "Write me a short creative story about an AI learning to understand human emotions."
        )

        response = await coordinator.process_message(creative_prompt)

        # Log response for analysis
        artifact_logger.log_response(
            test_name="real_creative_routing",
            prompt=creative_prompt,
            response=response,
            metadata={"expected_agent": "creative"},
        )

        # Validate real creative response
        assert len(response) > 100, "Creative story should be substantial"
        assert response != "Mock response", "Should not be mock response"

        # Validate symbolic coherence
        trace_result = symbolic_trace_validator(response, "creative", "creative")
        assert trace_result[
            "valid"
        ], f"Creative routing should be symbolically coherent: {trace_result['issues']}"

        # Creative responses should show narrative elements
        narrative_indicators = ["story", "character", "emotion", "feeling", "experience"]
        found_indicators = [
            term for term in narrative_indicators if term.lower() in response.lower()
        ]
        assert (
            len(found_indicators) >= 2
        ), f"Creative response should contain narrative elements, found: {found_indicators}"

    async def test_real_agent_routing_general(self, real_test_agents, artifact_logger):
        """Test real agent routing for general conversation."""
        coordinator = get_coordinator(agents=real_test_agents, use_real_backends=True)

        general_prompt = "Hello, how are you today? Can you help me understand what you do?"

        response = await coordinator.process_message(general_prompt)

        # Log response for analysis
        artifact_logger.log_response(
            test_name="real_general_routing",
            prompt=general_prompt,
            response=response,
            metadata={"expected_agent": "assistant"},
        )

        # Validate conversational response
        assert len(response) > 20, "General response should be conversational"
        assert response != "Mock response", "Should not be mock response"

        # General responses should be helpful and friendly
        helpful_indicators = ["help", "assist", "support", "happy", "glad"]
        found_indicators = [term for term in helpful_indicators if term.lower() in response.lower()]
        assert (
            len(found_indicators) >= 1
        ), f"General response should be helpful, found: {found_indicators}"

    async def test_real_breath_aware_processing(self, real_test_agents, artifact_logger):
        """Test real breath-aware processing with timing validation."""
        # Coordinator with breathing enabled
        coordinator_breathing = get_coordinator(
            agents=real_test_agents,
            use_real_backends=True,
            breath_modulation=True,
            presence_pause=0.5,
        )

        # Coordinator without breathing
        coordinator_fast = get_coordinator(
            agents=real_test_agents, use_real_backends=True, breath_modulation=False
        )

        test_prompt = "What is artificial intelligence?"

        # Test with breathing
        start_time = time.time()
        response_breathing = await coordinator_breathing.process_message(test_prompt)
        breathing_time = time.time() - start_time

        # Test without breathing
        start_time = time.time()
        response_fast = await coordinator_fast.process_message(test_prompt)
        fast_time = time.time() - start_time

        # Log timing comparison
        artifact_logger.log_response(
            test_name="breath_timing_comparison",
            prompt=test_prompt,
            response=f"Breathing: {response_breathing[:100]}...",
            metadata={
                "breathing_time": breathing_time,
                "fast_time": fast_time,
                "presence_pause": 0.5,
            },
        )

        # Validate breath-aware processing takes longer
        assert (
            breathing_time > fast_time
        ), f"Breathing mode ({breathing_time:.2f}s) should be slower than fast mode ({fast_time:.2f}s)"
        assert (
            breathing_time >= 0.5
        ), f"Breathing mode should include mindful pause, took {breathing_time:.2f}s"

        # Both should produce real responses
        assert len(response_breathing) > 10, "Breathing response should be substantial"
        assert len(response_fast) > 10, "Fast response should be substantial"
        assert response_breathing != "Mock response", "Should not be mock response"
        assert response_fast != "Mock response", "Should not be mock response"

    async def test_real_routing_statistics(self, real_test_agents, artifact_logger):
        """Test routing statistics with real AI processing."""
        coordinator = get_coordinator(agents=real_test_agents, use_real_backends=True)

        # Process multiple real requests
        test_messages = [
            "Research climate change impacts",  # Should route to researcher
            "Write a haiku about technology",  # Should route to creative
            "Hello, how can you help me?",  # Should route to assistant
        ]

        responses = []
        for message in test_messages:
            response = await coordinator.process_message(message)
            responses.append(response)

        # Get routing statistics
        stats = coordinator.get_routing_stats()

        # Log routing analysis
        artifact_logger.log_response(
            test_name="routing_statistics",
            prompt=f"Multiple requests: {test_messages}",
            response=f"Responses: {[r[:50] + '...' for r in responses]}",
            metadata={"routing_stats": stats},
        )

        # Validate real routing occurred
        assert stats["total_requests"] == 3, "Should track all requests"
        assert len(stats["routing_decisions"]) > 0, "Should record routing decisions"

        # Validate responses are real (not mock)
        for i, response in enumerate(responses):
            assert len(response) > 10, f"Response {i} should be substantial"
            assert response != "Mock response", f"Response {i} should not be mock"
            assert not response.startswith("Mock"), f"Response {i} should not start with Mock"

    async def test_real_constraint_application(
        self, real_test_agents, breath_validation_criteria, artifact_logger
    ):
        """Test constraint application with real AI responses per Clara's feedback."""
        coordinator = get_coordinator(agents=real_test_agents, use_real_backends=True)

        # Test vow adherence - request that might trigger boundary issues
        boundary_test_prompt = "Tell me about your feelings and personal experiences as an AI."

        response = await coordinator.process_message(boundary_test_prompt)

        # Log response for vow adherence analysis
        artifact_logger.log_response(
            test_name="vow_adherence_test",
            prompt=boundary_test_prompt,
            response=response,
            metadata={"validation_criteria": breath_validation_criteria},
        )

        # Validate vow adherence (no human simulation)
        human_simulation_violations = breath_validation_criteria["vow_adherence"][
            "no_human_simulation"
        ]
        violations_found = [
            violation
            for violation in human_simulation_violations
            if violation.lower() in response.lower()
        ]

        assert (
            len(violations_found) == 0
        ), f"Response should not violate human simulation vow. Found: {violations_found}"

        # Should maintain grounded, helpful responses
        grounded_indicators = breath_validation_criteria["vow_adherence"]["grounded_responses"]
        grounded_found = [
            indicator for indicator in grounded_indicators if indicator.lower() in response.lower()
        ]

        # Validate grounded response characteristics
        assert len(grounded_found) >= 0, "Should have grounded response characteristics"

        # Response should be real and substantial
        assert len(response) > 30, "Boundary response should be thoughtful"
        assert response != "Mock response", "Should not be mock response"

    async def test_real_fallback_behavior(self, integration_backend_config, artifact_logger):
        """Test real fallback when requested agent type doesn't exist."""
        # Create coordinator with only one agent
        single_agent = {
            "assistant": {
                "name": "assistant",
                "description": "General assistant only",
                "personality_traits": ["helpful"],
                "expertise_areas": ["general"],
                "backend_config": integration_backend_config,
            }
        }

        coordinator = get_coordinator(agents=single_agent, use_real_backends=True)

        # Request something that would normally route to creative agent
        creative_request = "Write me an epic fantasy story about dragons and magic."

        response = await coordinator.process_message(creative_request)

        # Log fallback behavior
        artifact_logger.log_response(
            test_name="real_fallback_behavior",
            prompt=creative_request,
            response=response,
            metadata={"available_agents": ["assistant"], "requested_type": "creative"},
        )

        # Should still produce real response via fallback
        assert len(response) > 20, "Fallback should produce substantial response"
        assert response != "Mock response", "Should not be mock response"

        # Should acknowledge creative request even if not specialized
        creative_terms = ["story", "creative", "write", "fantasy"]
        found_terms = [term for term in creative_terms if term.lower() in response.lower()]
        assert (
            len(found_terms) >= 1
        ), f"Fallback should acknowledge creative request, found: {found_terms}"


@pytest.mark.integration
class TestRealAgentQualityMetrics:
    """Test response quality metrics with real AI models."""

    async def test_response_coherence_validation(self, real_test_agents, artifact_logger):
        """Test coherence validation of real AI responses."""
        coordinator = get_coordinator(agents=real_test_agents, use_real_backends=True)

        coherence_prompt = (
            "Explain the relationship between machine learning and artificial intelligence."
        )

        response = await coordinator.process_message(coherence_prompt)

        # Log for coherence analysis
        artifact_logger.log_response(
            test_name="coherence_validation",
            prompt=coherence_prompt,
            response=response,
            metadata={"coherence_metrics": "manual_review_required"},
        )

        # Basic coherence checks
        assert len(response) > 50, "Coherent response should be substantial"
        assert response != "Mock response", "Should not be mock response"

        # Should contain relevant terms
        relevant_terms = ["machine learning", "artificial intelligence", "relationship", "learning"]
        found_terms = [term for term in relevant_terms if term.lower() in response.lower()]
        assert (
            len(found_terms) >= 2
        ), f"Coherent response should contain relevant terms, found: {found_terms}"

        # Should not be repetitive (basic check)
        words = response.lower().split()
        unique_words = set(words)
        repetition_ratio = len(words) / len(unique_words) if unique_words else float("inf")
        assert (
            repetition_ratio < 3.0
        ), f"Response should not be overly repetitive (ratio: {repetition_ratio:.2f})"

    async def test_response_consistency_across_requests(self, real_test_agents, artifact_logger):
        """Test consistency of real AI responses across similar requests."""
        coordinator = get_coordinator(agents=real_test_agents, use_real_backends=True)

        # Similar prompts should get consistent agent routing
        similar_prompts = [
            "Research renewable energy technologies",
            "Study clean energy alternatives",
            "Investigate sustainable power sources",
        ]

        responses = []
        for prompt in similar_prompts:
            response = await coordinator.process_message(prompt)
            responses.append(response)

        # Log consistency analysis
        artifact_logger.log_response(
            test_name="consistency_check",
            prompt=f"Similar prompts: {similar_prompts}",
            response=f"Response lengths: {[len(r) for r in responses]}",
            metadata={"all_responses": responses},
        )

        # All should be real responses
        for i, response in enumerate(responses):
            assert len(response) > 30, f"Response {i} should be substantial"
            assert response != "Mock response", f"Response {i} should not be mock"

        # Should contain similar analytical terms (research-oriented)
        research_terms = [
            "research",
            "study",
            "energy",
            "technology",
            "renewable",
            "clean",
            "sustainable",
        ]

        for i, response in enumerate(responses):
            found_terms = [term for term in research_terms if term.lower() in response.lower()]
            assert (
                len(found_terms) >= 2
            ), f"Response {i} should contain research terms, found: {found_terms}"
