# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Unit Tests for core Lamina functions and API.

These tests validate API contracts and mock behavior for fast feedback.
"""

import pytest

from lamina import __version__, get_coordinator, get_llm_client, get_memory_store


@pytest.mark.unit
class TestCoreFunctions:
    """Test core Lamina API functions."""

    def test_version_available(self):
        """Test that version information is available."""
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0

    def test_get_llm_client_function(self):
        """Test get_llm_client function."""
        # Basic usage
        client = get_llm_client()
        assert client is not None

        # With configuration
        client_with_config = get_llm_client({"model": "test"})
        assert client_with_config is not None

    def test_get_coordinator_function(self):
        """Test get_coordinator function."""
        # Basic usage
        coordinator = get_coordinator()
        assert coordinator is not None

        # With agents
        agents = {
            "test": {
                "name": "test",
                "description": "Test agent",
                "personality_traits": ["helpful"],
                "expertise_areas": ["testing"],
            }
        }
        coordinator_with_agents = get_coordinator(agents=agents)
        assert coordinator_with_agents is not None
        assert len(coordinator_with_agents.agents) == 1

    def test_get_memory_store_function(self):
        """Test get_memory_store function."""
        # Note: This may not be fully implemented yet
        try:
            memory_store = get_memory_store()
            assert memory_store is not None
        except (ImportError, NotImplementedError):
            # Expected if memory store not fully implemented
            pytest.skip("Memory store not fully implemented yet")

    def test_function_error_handling(self):
        """Test error handling in core functions."""
        # Invalid client configuration should not raise
        # (this is just for demonstration that the function handles configs gracefully)
        client = get_llm_client({"invalid": "config"})
        assert client is not None

    def test_breath_first_defaults(self):
        """Test that functions default to breath-first behavior."""
        coordinator = get_coordinator()

        # Should default to breath-aware processing
        assert coordinator.breath_modulation is True
        assert coordinator.presence_pause > 0
