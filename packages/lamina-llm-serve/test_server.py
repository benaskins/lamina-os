#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""Pytest based checks for the LLM server API."""

from __future__ import annotations

import threading
import time
from collections.abc import Generator

import pytest
import requests
from werkzeug.serving import make_server

from lamina_llm_serve.server import LLMServer


@pytest.fixture(scope="module")
def llm_server() -> Generator[str, None, None]:
    """Run ``LLMServer`` in a background thread for the tests."""

    server = LLMServer()
    http_server = make_server("127.0.0.1", 0, server.app)
    thread = threading.Thread(target=http_server.serve_forever)
    thread.start()

    base_url = f"http://127.0.0.1:{http_server.server_port}"

    for _ in range(20):
        try:
            if requests.get(f"{base_url}/health", timeout=1).status_code == 200:
                break
        except Exception:  # pragma: no cover - server not yet ready
            time.sleep(0.1)
    else:  # pragma: no cover - startup failure
        http_server.shutdown()
        thread.join(timeout=1)
        pytest.fail("LLMServer failed to start")

    yield base_url

    http_server.shutdown()
    thread.join(timeout=1)


def test_health_endpoint(llm_server: str) -> None:
    """Verify that the health endpoint reports server status."""

    response = requests.get(f"{llm_server}/health", timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "models" in data
    assert "active_servers" in data


def test_models_endpoint(llm_server: str) -> None:
    """Ensure the models endpoint returns registry information."""

    response = requests.get(f"{llm_server}/models", timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data.get("models"), dict)
    assert "total" in data
    assert "available" in data
    assert "active" in data


def test_backends_endpoint(llm_server: str) -> None:
    """Check backend configuration reporting."""

    response = requests.get(f"{llm_server}/backends", timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert "backends" in data
    assert "available" in data
    assert "total_configured" in data
    assert "total_available" in data


def test_suggest_endpoint(llm_server: str) -> None:
    """Request a model suggestion and verify the response."""

    response = requests.post(
        f"{llm_server}/suggest", json={"use_case": "conversational"}, timeout=5
    )
    assert response.status_code == 200
    data = response.json()
    assert "suggested" in data
    assert "model_info" in data
    assert "available" in data


def test_model_info_endpoint(llm_server: str) -> None:
    """Retrieve metadata for a known model from the registry."""

    response = requests.get(f"{llm_server}/models/llama3.2-3b-q4_k_m", timeout=5)
    assert response.status_code == 200
    data = response.json()
    assert "backend" in data
    assert "path" in data
    assert "available" in data


def test_chat_completions_validation(llm_server: str) -> None:
    """Validate error handling in the OpenAI chat completions endpoint."""

    resp = requests.post(
        f"{llm_server}/v1/chat/completions",
        json={"messages": [{"role": "user", "content": "hi"}]},
        timeout=5,
    )
    assert resp.status_code == 400
    assert "error" in resp.json()

    resp = requests.post(
        f"{llm_server}/v1/chat/completions",
        json={"model": "test"},
        timeout=5,
    )
    assert resp.status_code == 400
    assert "error" in resp.json()

    resp = requests.post(f"{llm_server}/v1/chat/completions", data="invalid", timeout=5)
    assert resp.status_code == 400

    resp = requests.post(
        f"{llm_server}/v1/chat/completions",
        json={"model": "does-not-exist", "messages": [{"role": "user", "content": "hi"}]},
        timeout=5,
    )
    assert resp.status_code == 404
    data = resp.json()
    assert "error" in data
    assert "available_models" in data
