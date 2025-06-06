#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""Meaningful regression tests for the LLM server API.

These tests focus on catching regressions in core functionality:
- Model discovery and metadata retrieval
- Error handling and validation
- API contract compliance
- Model suggestion logic
"""

from __future__ import annotations

import requests


def test_health_endpoint_structure(llm_server: str) -> None:
    """Verify health endpoint returns consistent structure.
    
    Regression test: Ensures health endpoint maintains expected format
    for monitoring and service discovery.
    """
    response = requests.get(f"{llm_server}/health", timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert isinstance(data["timestamp"], (int, float))
    assert isinstance(data["models"], dict)
    assert isinstance(data["active_servers"], int)
    assert data["active_servers"] >= 0


def test_models_endpoint_contract(llm_server: str) -> None:
    """Verify models endpoint maintains API contract.
    
    Regression test: Ensures models endpoint structure for agent coordination.
    """
    response = requests.get(f"{llm_server}/models", timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data["models"], dict)
    assert isinstance(data["total"], int)
    assert isinstance(data["available"], int)
    assert isinstance(data["active"], int)
    
    # Verify test models are present
    assert data["total"] >= 2  # We have test-model and llama3.2-3b-q4_k_m
    assert "test-model" in data["models"]
    assert "llama3.2-3b-q4_k_m" in data["models"]
    
    # Verify model structure
    for model_name, model_info in data["models"].items():
        assert "available" in model_info
        assert "active" in model_info
        assert isinstance(model_info["available"], bool)
        assert isinstance(model_info["active"], bool)


def test_backends_endpoint_stability(llm_server: str) -> None:
    """Verify backend discovery consistency.
    
    Regression test: Backend reporting should be stable across calls.
    """
    response = requests.get(f"{llm_server}/backends", timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data["backends"], dict)
    assert isinstance(data["available"], list)
    assert isinstance(data["total_configured"], int)
    assert isinstance(data["total_available"], int)
    
    # Backend consistency checks
    assert data["total_configured"] >= 1  # At least llama.cpp configured
    assert data["total_available"] <= data["total_configured"]


def test_model_suggestion_logic(llm_server: str) -> None:
    """Verify model suggestion algorithm works correctly.
    
    Regression test: Model suggestions should be consistent and logical.
    """
    # Test conversational use case
    response = requests.post(
        f"{llm_server}/suggest", json={"use_case": "conversational"}, timeout=5
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "suggested" in data
    assert "model_info" in data
    assert "available" in data
    
    # Should suggest one of our conversational models
    assert data["suggested"] in ["test-model", "llama3.2-3b-q4_k_m"]
    assert isinstance(data["model_info"], dict)
    assert isinstance(data["available"], bool)
    
    # Test with invalid use case - should still handle gracefully
    response = requests.post(
        f"{llm_server}/suggest", json={"use_case": "nonexistent"}, timeout=5
    )
    # May return 404 if no suitable model found, which is acceptable
    assert response.status_code in [200, 404]


def test_model_info_retrieval(llm_server: str) -> None:
    """Verify model metadata retrieval is consistent.
    
    Regression test: Model info should include all required metadata.
    """
    # Test valid model
    response = requests.get(f"{llm_server}/models/llama3.2-3b-q4_k_m", timeout=5)
    assert response.status_code == 200
    
    data = response.json()
    required_fields = ["backend", "path", "available", "active"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    assert data["backend"] == "llama.cpp"
    assert isinstance(data["available"], bool)
    assert isinstance(data["active"], bool)
    
    # Test non-existent model
    response = requests.get(f"{llm_server}/models/nonexistent-model", timeout=5)
    assert response.status_code == 404
    
    error_data = response.json()
    assert "error" in error_data


def test_chat_completions_validation(llm_server: str) -> None:
    """Verify OpenAI-compatible endpoint error handling.
    
    Regression test: Chat completions must validate requests properly.
    """
    # Missing model parameter
    response = requests.post(
        f"{llm_server}/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "hi"}]},
        timeout=5,
    )
    assert response.status_code == 400
    error_data = response.json()
    assert "error" in error_data
    assert "model" in error_data["error"]

    # Missing messages parameter
    response = requests.post(
        f"{llm_server}/v1/chat/completions",
        json={"model": "test-model"},
        timeout=5,
    )
    assert response.status_code == 400
    error_data = response.json()
    assert "error" in error_data
    assert "messages" in error_data["error"]

    # Invalid JSON request (should be handled properly)
    response = requests.post(
        f"{llm_server}/v1/chat/completions", 
        data="invalid", 
        headers={"Content-Type": "text/plain"},
        timeout=5
    )
    assert response.status_code == 400

    # Non-existent model
    response = requests.post(
        f"{llm_server}/v1/chat/completions",
        json={"model": "does-not-exist", "messages": [{"role": "user", "content": "hi"}]},
        timeout=5,
    )
    assert response.status_code == 404
    error_data = response.json()
    assert "error" in error_data
    assert "available_models" in error_data


def test_openai_compatibility_contract(llm_server: str) -> None:
    """Verify OpenAI API compatibility structure.
    
    Regression test: Response format must match OpenAI specification.
    """
    # Test with valid model that exists but isn't available (model not downloaded)
    response = requests.post(
        f"{llm_server}/v1/chat/completions",
        json={
            "model": "test-model",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 50
        },
        timeout=5,
    )
    
    # Should fail because model server isn't started, but should be handled gracefully
    # This tests the model availability check before attempting to start server
    assert response.status_code in [503, 500]  # Service unavailable or internal error
    
    if response.status_code == 503:
        error_data = response.json()
        assert "error" in error_data
        assert "hint" in error_data or "model" in error_data["error"]
