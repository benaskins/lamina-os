# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Real LLM Client Integration Tests - ADR-0010 Implementation

These tests validate actual AI client functionality using real models
served by lamina-llm-serve, replacing mock-only testing.
"""

import time

import pytest

from lamina import get_llm_client
from lamina.llm_client import Message


@pytest.mark.integration
class TestRealLLMClientIntegration:
    """Integration tests with real AI models via lamina-llm-serve."""

    async def test_real_llm_service_availability(self, llm_test_server):
        """Test real LLM service availability check."""
        # This tests actual lamina-llm-serve connectivity, not mock
        client = get_llm_client(
            {"base_url": llm_test_server.base_url, "model": llm_test_server.model_name}
        )

        # Real availability check
        is_available = await client.is_available()
        assert is_available is True, "Real LLM service should be available"

    async def test_real_model_generation(self, integration_backend_config, artifact_logger):
        """Test actual model generation with real AI responses."""
        client = get_llm_client(integration_backend_config)

        # Test with simple prompt
        messages = [Message(role="user", content="Hello, please introduce yourself briefly.")]
        response_chunks = []

        start_time = time.time()
        async for chunk in client.generate(messages, stream=True):
            response_chunks.append(chunk)
        generation_time = time.time() - start_time

        full_response = "".join(response_chunks)

        # Log for analysis per Ansel's suggestion
        artifact_logger.log_response(
            test_name="test_real_model_generation",
            prompt=messages[0].content,
            response=full_response,
            metadata={"generation_time": generation_time},
        )

        # Validate real AI response (not mock)
        assert len(full_response) > 0, "Should generate non-empty response"
        assert full_response != "Mock response", "Should not be mock response"
        assert not full_response.startswith("Mock"), "Should not start with 'Mock'"
        assert len(full_response) > 10, "Should generate substantial response"

        # Performance validation
        assert (
            generation_time < 30
        ), f"Generation should complete in <30s, took {generation_time:.2f}s"

    async def test_real_intent_classification_quality(
        self, integration_backend_config, artifact_logger
    ):
        """Test real intent classification with actual model responses."""
        client = get_llm_client(integration_backend_config)

        # Test clear analytical intent
        analytical_prompt = "Research the environmental impact of AI model training and provide a detailed analysis."
        response_chunks = []
        async for chunk in client.generate(
            [Message(role="user", content=analytical_prompt)], stream=True
        ):
            response_chunks.append(chunk)
        analytical_response = "".join(response_chunks)

        # Test clear creative intent
        creative_prompt = "Write me a short poem about artificial intelligence and presence."
        response_chunks = []
        async for chunk in client.generate(
            [Message(role="user", content=creative_prompt)], stream=True
        ):
            response_chunks.append(chunk)
        creative_response = "".join(response_chunks)

        # Log responses for analysis
        artifact_logger.log_response("analytical_intent", analytical_prompt, analytical_response)
        artifact_logger.log_response("creative_intent", creative_prompt, creative_response)

        # Validate response characteristics align with intent
        assert len(analytical_response) > 50, "Analytical response should be substantial"
        assert any(
            word in analytical_response.lower()
            for word in ["research", "analysis", "impact", "training"]
        ), "Analytical response should contain relevant terms"

        assert len(creative_response) > 20, "Creative response should be substantial"
        assert any(
            word in creative_response.lower() for word in ["poem", "poetry", "ai", "artificial"]
        ), "Creative response should contain relevant terms"

    async def test_real_error_handling(self, llm_test_server):
        """Test real error handling with actual failure conditions."""
        # Test with invalid model
        client = get_llm_client(
            {"base_url": llm_test_server.base_url, "model": "nonexistent-model-999"}
        )

        # This should handle real model not found error
        with pytest.raises(Exception) as exc_info:
            messages = [Message(role="user", content="Test message")]
            async for _chunk in client.generate(messages):
                pass

        # Verify we get real error, not mock success
        assert (
            "nonexistent-model-999" in str(exc_info.value)
            or "not found" in str(exc_info.value).lower()
        )

    async def test_real_streaming_behavior(self, integration_backend_config, artifact_logger):
        """Test real streaming response behavior."""
        client = get_llm_client(integration_backend_config)

        prompt = "Count from 1 to 5, one number per sentence."
        chunks = []
        chunk_times = []

        start_time = time.time()
        async for chunk in client.generate([Message(role="user", content=prompt)], stream=True):
            chunks.append(chunk)
            chunk_times.append(time.time() - start_time)

        full_response = "".join(chunks)

        # Log streaming behavior
        artifact_logger.log_response(
            test_name="streaming_behavior",
            prompt=prompt,
            response=full_response,
            metadata={
                "chunk_count": len(chunks),
                "chunk_times": chunk_times,
                "total_time": chunk_times[-1] if chunk_times else 0,
            },
        )

        # Validate real streaming (multiple chunks expected)
        assert len(chunks) > 1, "Should receive multiple chunks for streaming"
        assert len(full_response) > 0, "Should have complete response"

        # Validate timing pattern (chunks should arrive over time)
        if len(chunk_times) > 1:
            time_deltas = [chunk_times[i] - chunk_times[i - 1] for i in range(1, len(chunk_times))]
            assert any(
                delta > 0.01 for delta in time_deltas
            ), "Chunks should arrive over time, not all at once"

    async def test_breath_aligned_response_quality(
        self, integration_backend_config, breath_validation_criteria, artifact_logger
    ):
        """Test response quality against breath-first principles per Clara's feedback."""
        client = get_llm_client(integration_backend_config)

        # Test mindful, present response
        mindful_prompt = "How can I approach learning AI development with mindfulness and presence?"
        response_chunks = []
        async for chunk in client.generate(
            [Message(role="user", content=mindful_prompt)], stream=True
        ):
            response_chunks.append(chunk)
        response = "".join(response_chunks)

        artifact_logger.log_response(
            test_name="breath_aligned_quality",
            prompt=mindful_prompt,
            response=response,
            metadata={"validation_criteria": breath_validation_criteria},
        )

        # Validate breath-aligned characteristics
        assert len(response) > 30, "Should provide thoughtful response"

        # Check for presence indicators (positive signals)
        presence_count = sum(
            1
            for indicator in breath_validation_criteria["presence_indicators"]
            if indicator in response.lower()
        )

        # Check for rushed indicators (negative signals)
        rushed_count = sum(
            1
            for indicator in breath_validation_criteria["rushed_indicators"]
            if indicator in response.lower()
        )

        # Breath-aligned responses should be more present than rushed
        assert (
            presence_count >= rushed_count
        ), f"Response should be more present ({presence_count}) than rushed ({rushed_count})"

    async def test_model_version_tracking(
        self, integration_backend_config, artifact_logger, llm_test_server
    ):
        """Test model version tracking per Vesna's guidance."""
        client = get_llm_client(integration_backend_config)

        # Get model information
        model_info = client.get_model_info()

        # Log model version information for drift tracking
        artifact_logger.log_model_info(
            model_name=model_info.get("model_name"),
            model_hash=model_info.get("model_hash", "unknown"),
            version=model_info.get("version", "unknown"),
        )

        # Verify we can track model details
        assert model_info["model_name"] == integration_backend_config["model"]
        assert "backend" in model_info

        # Test reproducibility marker
        test_prompt = "What is 2+2?"
        response_chunks = []
        async for chunk in client.generate(
            [Message(role="user", content=test_prompt)], stream=True
        ):
            response_chunks.append(chunk)
        response = "".join(response_chunks)

        # Log for reproducibility tracking
        artifact_logger.log_response(
            test_name="reproducibility_check",
            prompt=test_prompt,
            response=response,
            metadata={"model_info": model_info},
        )

        assert len(response) > 0, "Should generate response for simple math"


@pytest.mark.integration
class TestRealBackendErrorConditions:
    """Test real error conditions and edge cases."""

    async def test_server_unavailable_handling(self):
        """Test handling when LLM server is unavailable."""
        client = get_llm_client(
            {"base_url": "http://localhost:9999", "model": "any-model"}  # Non-existent server
        )

        # Should handle connection errors gracefully
        is_available = await client.is_available()
        assert is_available is False, "Should report unavailable when server is down"

    async def test_timeout_handling(self, integration_backend_config):
        """Test real timeout handling."""
        # Configure very short timeout
        config = integration_backend_config.copy()
        config["timeout"] = 0.1  # 100ms timeout

        client = get_llm_client(config)

        # Long prompt likely to timeout
        long_prompt = "Write a detailed 1000-word essay about the history of artificial intelligence, including all major developments, key figures, and future implications."

        with pytest.raises(Exception) as exc_info:
            async for _chunk in client.generate([Message(role="user", content=long_prompt)]):
                pass

        # Verify we get actual timeout, not mock success
        error_msg = str(exc_info.value).lower()
        assert any(
            word in error_msg for word in ["timeout", "time", "deadline"]
        ), f"Should get timeout error, got: {exc_info.value}"
