#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""Pytest configuration and fixtures for lamina-llm-serve tests."""

import tempfile
import threading
import time
from collections.abc import Generator
from pathlib import Path

import pytest
import requests
import yaml
from werkzeug.serving import make_server

from lamina_llm_serve.server import LLMServer


@pytest.fixture(scope="module")
def test_models_yaml() -> Generator[str, None, None]:
    """Create a temporary models.yaml file for testing."""
    
    test_config = {
        "models": {
            "test-model": {
                "path": "test-model/model.gguf",
                "backend": "llama.cpp",
                "size": "1.0GB",
                "description": "Test model for regression testing",
                "quantization": "Q4_K_M",
                "use_cases": ["conversational", "testing"]
            },
            "llama3.2-3b-q4_k_m": {
                "path": "llama3.2-3b-q4_k_m/Llama-3.2-3B-Instruct-Q4_K_M.gguf",
                "backend": "llama.cpp",
                "size": "2.0GB",
                "description": "Efficient 3B parameter model, good for general conversation",
                "quantization": "Q4_K_M",
                "use_cases": ["conversational", "reasoning"]
            }
        },
        "categories": {
            "conversational": ["test-model", "llama3.2-3b-q4_k_m"],
            "testing": ["test-model"]
        },
        "backends": {
            "llama.cpp": {
                "executable": "llama-server",
                "args": ["--model", "{model_path}", "--port", "{port}"]
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(test_config, f)
        manifest_path = f.name
    
    yield manifest_path
    
    # Cleanup
    Path(manifest_path).unlink(missing_ok=True)


@pytest.fixture(scope="module")
def test_models_dir() -> Generator[str, None, None]:
    """Create a temporary models directory for testing."""
    
    with tempfile.TemporaryDirectory() as models_dir:
        # Create fake model files for testing
        test_model_dir = Path(models_dir) / "test-model"
        test_model_dir.mkdir()
        (test_model_dir / "model.gguf").touch()
        
        llama_model_dir = Path(models_dir) / "llama3.2-3b-q4_k_m"
        llama_model_dir.mkdir()
        (llama_model_dir / "Llama-3.2-3B-Instruct-Q4_K_M.gguf").touch()
        
        yield str(models_dir)


@pytest.fixture(scope="module")
def llm_server(test_models_yaml: str, test_models_dir: str) -> Generator[str, None, None]:
    """Run LLMServer in a background thread for the tests."""

    server = LLMServer(manifest_path=test_models_yaml, models_dir=test_models_dir)
    http_server = make_server("127.0.0.1", 0, server.app)
    thread = threading.Thread(target=http_server.serve_forever)
    thread.start()

    base_url = f"http://127.0.0.1:{http_server.server_port}"

    # Wait for server to be ready
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