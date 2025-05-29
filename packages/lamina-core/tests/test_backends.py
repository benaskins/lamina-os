# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Tests for AI backends and provider integrations.
"""

import pytest

from lamina import get_backend


class TestBackends:
    """Test AI backend integrations."""

    def test_mock_backend_creation(self):
        """Test mock backend creation and configuration."""
        backend = get_backend("mock", {"model": "test-model"})
        assert backend is not None
        assert backend.model_name == "test-model"

    @pytest.mark.asyncio
    async def test_mock_backend_generation(self):
        """Test mock backend response generation."""
        backend = get_backend("mock", {"model": "test-model"})

        messages = ["Hello, how are you?"]
        response_chunks = []

        async for chunk in backend.generate(messages, stream=True):
            response_chunks.append(chunk)

        # Should get response chunks
        assert len(response_chunks) > 0
        full_response = "".join(response_chunks)
        assert "Mock response" in full_response
        assert "test-model" in full_response

    @pytest.mark.asyncio
    async def test_mock_backend_availability(self):
        """Test mock backend availability check."""
        backend = get_backend("mock")
        assert await backend.is_available() is True

    @pytest.mark.asyncio
    async def test_mock_backend_model_management(self):
        """Test mock backend model loading/unloading."""
        backend = get_backend("mock")
        assert await backend.load_model() is True
        assert await backend.unload_model() is True

    def test_backend_registry(self):
        """Test that backend registry includes expected providers."""
        from lamina.backends import BACKENDS, HUGGINGFACE_AVAILABLE, list_backends

        # Should have mock backend
        assert "mock" in BACKENDS

        # Should list available backends
        backends = list_backends()
        assert "mock" in backends
        assert "ollama" in backends

        # HuggingFace only available if dependencies installed
        if HUGGINGFACE_AVAILABLE:
            assert "huggingface" in backends

    def test_invalid_backend_provider(self):
        """Test error handling for invalid backend provider."""
        with pytest.raises(ValueError) as exc_info:
            get_backend("nonexistent-provider")

        assert "Unknown backend" in str(exc_info.value)
        assert "nonexistent-provider" in str(exc_info.value)

    def test_backend_configuration(self):
        """Test backend configuration handling."""
        # With explicit config
        backend1 = get_backend("mock", {"model": "custom-model"})
        assert backend1.model_name == "custom-model"

        # With default config
        backend2 = get_backend("mock")
        assert backend2.model_name == "mock-model"  # Default value
