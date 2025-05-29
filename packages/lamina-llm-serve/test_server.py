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
import requests
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from server import LLMServer
import threading
import time

def test_server_api():
    """Test the server API endpoints"""
    
    # Start server in a separate thread
    server = LLMServer()
    
    def run_server():
        server.app.run(host='127.0.0.1', port=8080, debug=False)
    
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
        response = requests.post(f"{base_url}/suggest", 
                               json={"use_case": "conversational"})
        print(f"✅ Suggest: {response.status_code}")
        if response.status_code == 200:
            suggest_data = response.json()
            print(f"   Suggested: {suggest_data.get('suggested', 'None')}")
        elif response.status_code == 404:
            print(f"   No suitable model found (expected - no models available)")
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
    
    print("\n🎯 Server API test completed!")

if __name__ == "__main__":
    test_server_api()