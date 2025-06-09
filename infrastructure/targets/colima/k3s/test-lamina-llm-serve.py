#!/usr/bin/env python3
"""
Test script for Lamina LLM Serve deployment.
Tests the chat endpoint and model serving functionality.
"""

import requests
import json
import time
import sys
from typing import Dict, Any


def test_health_endpoint(base_url: str) -> bool:
    """Test the health endpoint."""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✓ Health endpoint: OK")
            return True
        else:
            print(f"✗ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health endpoint error: {e}")
        return False


def test_models_endpoint(base_url: str) -> bool:
    """Test the models listing endpoint."""
    try:
        response = requests.get(f"{base_url}/models", timeout=10)
        if response.status_code == 200:
            models = response.json()
            print(f"✓ Models endpoint: Found {len(models)} models")
            for model_name in models:
                print(f"  - {model_name}")
            return True
        else:
            print(f"✗ Models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Models endpoint error: {e}")
        return False


def test_chat_endpoint(base_url: str, model_name: str = "llama3.2-1b-q4_k_m") -> bool:
    """Test the chat endpoint with a simple prompt."""
    try:
        # Test data
        chat_data = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": "Hello! Please respond with just 'TEST SUCCESS' if you can understand this."}
            ],
            "temperature": 0.1,
            "max_tokens": 10
        }
        
        print(f"Testing chat endpoint with model: {model_name}")
        response = requests.post(
            f"{base_url}/chat/completions", 
            json=chat_data,
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {}).get("content", "")
                print(f"✓ Chat endpoint: Model responded")
                print(f"  Response: {message.strip()}")
                return True
            else:
                print(f"✗ Chat endpoint: Invalid response format")
                print(f"  Response: {result}")
                return False
        else:
            print(f"✗ Chat endpoint failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Chat endpoint error: {e}")
        return False


def test_model_info(base_url: str, model_name: str = "llama3.2-1b-q4_k_m") -> bool:
    """Test getting model information."""
    try:
        response = requests.get(f"{base_url}/models/{model_name}", timeout=10)
        if response.status_code == 200:
            info = response.json()
            print(f"✓ Model info endpoint: {model_name}")
            print(f"  Description: {info.get('description', 'N/A')}")
            print(f"  Size: {info.get('size', 'N/A')}")
            print(f"  Backend: {info.get('backend', 'N/A')}")
            return True
        else:
            print(f"✗ Model info endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Model info endpoint error: {e}")
        return False


def main():
    """Run all tests against the Lamina LLM Serve deployment."""
    
    # Try both local cluster service and Istio gateway
    test_urls = [
        "http://llm.lamina.local",  # Via Istio gateway
        "http://127.0.0.1:8000",   # Direct to service (if port-forwarded)
    ]
    
    print("🧪 Testing Lamina LLM Serve Deployment")
    print("=" * 50)
    
    successful_url = None
    
    # Find a working URL
    for url in test_urls:
        print(f"\n🔗 Testing connection to: {url}")
        if test_health_endpoint(url):
            successful_url = url
            break
        time.sleep(1)
    
    if not successful_url:
        print("\n❌ FAILED: Could not connect to any Lamina LLM Serve endpoint")
        print("\nTroubleshooting:")
        print("1. Check if lamina-llm-serve pods are running:")
        print("   kubectl get pods -n lamina-llm-serve")
        print("2. Check if Istio gateway is configured:")
        print("   kubectl get virtualservice -n lamina-llm-serve")
        print("3. For local testing, try port forwarding:")
        print("   kubectl port-forward -n lamina-llm-serve svc/lamina-llm-serve 8000:8000")
        sys.exit(1)
    
    print(f"\n✅ Connected to: {successful_url}")
    print(f"\n🧪 Running functional tests...")
    
    # Run all tests
    tests = [
        ("Models List", lambda: test_models_endpoint(successful_url)),
        ("Model Info", lambda: test_model_info(successful_url)),
        ("Chat Completion", lambda: test_chat_endpoint(successful_url)),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        results.append(test_func())
        time.sleep(1)
    
    # Summary
    print(f"\n🏁 Test Summary:")
    print(f"=" * 50)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 ALL TESTS PASSED ({passed}/{total})")
        print(f"✅ Lamina LLM Serve is working correctly!")
        sys.exit(0)
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total})")
        print(f"🔧 Check the deployment and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()