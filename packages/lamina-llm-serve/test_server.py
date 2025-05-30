#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Quick test of the LLM server API endpoints
"""

import sys
from pathlib import Path

import requests

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

import threading
import time

from lamina_llm_serve.server import LLMServer


def test_server_api():
    """Test the server API endpoints"""

    # Start server in a separate thread
    server = LLMServer()

    def run_server():
        server.app.run(host="127.0.0.1", port=8080, debug=False)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    time.sleep(2)

    base_url = "http://127.0.0.1:8080"

    print("🧪 Testing LLM Server API")
    print("=" * 40)

    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"   Models: {health_data.get('models', {})}")
            print(f"   Active servers: {health_data.get('active_servers', 0)}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

    # Test models endpoint
    try:
        response = requests.get(f"{base_url}/models")
        print(f"✅ Models list: {response.status_code}")
        if response.status_code == 200:
            models_data = response.json()
            print(f"   Total models: {models_data.get('total', 0)}")
            print(f"   Available: {models_data.get('available', 0)}")
            print(f"   Active: {models_data.get('active', 0)}")
    except Exception as e:
        print(f"❌ Models list failed: {e}")

    # Test backends endpoint
    try:
        response = requests.get(f"{base_url}/backends")
        print(f"✅ Backends: {response.status_code}")
        if response.status_code == 200:
            backends_data = response.json()
            print(f"   Configured: {backends_data.get('total_configured', 0)}")
            print(f"   Available: {backends_data.get('total_available', 0)}")
    except Exception as e:
        print(f"❌ Backends check failed: {e}")

    # Test suggest endpoint
    try:
        response = requests.post(f"{base_url}/suggest", json={"use_case": "conversational"})
        print(f"✅ Suggest: {response.status_code}")
        if response.status_code == 200:
            suggest_data = response.json()
            print(f"   Suggested: {suggest_data.get('suggested', 'None')}")
        elif response.status_code == 404:
            print("   No suitable model found (expected - no models available)")
    except Exception as e:
        print(f"❌ Suggest failed: {e}")

    # Test individual model info
    try:
        response = requests.get(f"{base_url}/models/llama3.2-3b-q4_k_m")
        print(f"✅ Model info: {response.status_code}")
        if response.status_code == 200:
            model_data = response.json()
            print(f"   Available: {model_data.get('available', False)}")
            print(f"   Backend: {model_data.get('backend', 'unknown')}")
    except Exception as e:
        print(f"❌ Model info failed: {e}")

    # Test chat completions endpoint
    print("\n" + "=" * 40)
    print("🧪 Testing Chat Completions API")
    print("=" * 40)

    test_chat_completions_api(base_url)

    print("\n🎯 Server API test completed!")


def test_chat_completions_api(base_url):
    """Test the OpenAI-compatible chat completions endpoint"""

    # Test 1: Invalid requests
    print("\n📋 Testing request validation...")

    # Missing model parameter
    try:
        response = requests.post(f"{base_url}/v1/chat/completions", json={
            "messages": [{"role": "user", "content": "Hello"}]
        })
        print(f"✅ Missing model param: {response.status_code} (expected 400)")
        if response.status_code == 400:
            error_data = response.json()
            print(f"   Error: {error_data.get('error', 'No error message')}")
    except Exception as e:
        print(f"❌ Missing model test failed: {e}")

    # Missing messages parameter
    try:
        response = requests.post(f"{base_url}/v1/chat/completions", json={
            "model": "test-model"
        })
        print(f"✅ Missing messages param: {response.status_code} (expected 400)")
        if response.status_code == 400:
            error_data = response.json()
            print(f"   Error: {error_data.get('error', 'No error message')}")
    except Exception as e:
        print(f"❌ Missing messages test failed: {e}")

    # Invalid JSON
    try:
        response = requests.post(f"{base_url}/v1/chat/completions", data="invalid json")
        print(f"✅ Invalid JSON: {response.status_code} (expected 400)")
    except Exception as e:
        print(f"❌ Invalid JSON test failed: {e}")

    # Test 2: Model not found
    print("\n📋 Testing model validation...")

    try:
        response = requests.post(f"{base_url}/v1/chat/completions", json={
            "model": "nonexistent-model",
            "messages": [{"role": "user", "content": "Hello"}]
        })
        print(f"✅ Nonexistent model: {response.status_code} (expected 404)")
        if response.status_code == 404:
            error_data = response.json()
            print(f"   Error: {error_data.get('error', 'No error message')}")
            available = error_data.get('available_models', [])
            print(f"   Available models: {len(available)} models listed")
    except Exception as e:
        print(f"❌ Nonexistent model test failed: {e}")

    # Test 3: Valid model from registry
    print("\n📋 Testing with registry models...")

    # First, get available models to test with
    try:
        models_response = requests.get(f"{base_url}/models")
        if models_response.status_code == 200:
            models_data = models_response.json()
            available_models = [name for name, info in models_data.get('models', {}).items()
                              if info.get('available', False)]

            if available_models:
                test_model = available_models[0]
                print(f"   Found available model for testing: {test_model}")

                # Test chat request with available model
                try:
                    response = requests.post(f"{base_url}/v1/chat/completions", json={
                        "model": test_model,
                        "messages": [
                            {"role": "user", "content": "Hello, please respond with just 'Hi'"}
                        ],
                        "stream": False
                    }, timeout=30)

                    print(f"✅ Chat with available model: {response.status_code}")

                    if response.status_code == 200:
                        # Try to parse as JSON (OpenAI format)
                        try:
                            chat_data = response.json()
                            print("   Response format: OpenAI-compatible JSON")
                            if 'choices' in chat_data:
                                print(f"   Choices: {len(chat_data['choices'])} choice(s)")
                            if 'usage' in chat_data:
                                print("   Usage tracking: Present")
                        except Exception:
                            print(f"   Response format: Raw text ({len(response.text)} chars)")

                    elif response.status_code == 503:
                        error_data = response.json()
                        print(f"   Model not on filesystem: {error_data.get('error', '')}")
                        print(f"   Hint: {error_data.get('hint', '')}")

                    elif response.status_code == 500:
                        error_data = response.json()
                        print(f"   Server error: {error_data.get('error', '')}")
                        # This is expected if backends aren't available

                except Exception as e:
                    print(f"❌ Chat request failed: {e}")
            else:
                print("   No available models found for testing")

                # Test with unavailable model from registry
                registry_models = list(models_data.get('models', {}).keys())
                if registry_models:
                    test_model = registry_models[0]
                    try:
                        response = requests.post(f"{base_url}/v1/chat/completions", json={
                            "model": test_model,
                            "messages": [{"role": "user", "content": "Hello"}]
                        })
                        print(f"✅ Unavailable model: {response.status_code} (expected 503)")
                        if response.status_code == 503:
                            error_data = response.json()
                            print(f"   Error: {error_data.get('error', '')}")
                            print(f"   Hint: {error_data.get('hint', '')}")
                    except Exception as e:
                        print(f"❌ Unavailable model test failed: {e}")

    except Exception as e:
        print(f"❌ Model testing failed: {e}")

    # Test 4: Streaming parameter
    print("\n📋 Testing streaming parameter...")

    try:
        response = requests.post(f"{base_url}/v1/chat/completions", json={
            "model": "llama3.2-1b-q4_k_m",  # Use known model from registry
            "messages": [{"role": "user", "content": "Hello"}],
            "stream": True
        })
        print(f"✅ Streaming request: {response.status_code}")
        if response.status_code == 200:
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Not set')}")
            print("   Response headers indicate streaming support")
        elif response.status_code in [500, 503]:
            print("   Expected error (backend/model not available)")
    except Exception as e:
        print(f"❌ Streaming test failed: {e}")


if __name__ == "__main__":
    test_server_api()
