#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Test script for LaminaLLMClient integration
"""

import asyncio
import sys
from pathlib import Path

# Add package to path for testing
sys.path.insert(0, str(Path(__file__).parent))

from lamina import get_llm_client
from lamina.llm_client import Message


async def test_llamaserve_client():
    """Test the LaminaLLMClient with real lamina-llm-serve."""

    print("🧪 Testing LaminaLLMClient Integration")
    print("=" * 50)

    # Configuration for lamina-llm-serve
    config = {
        "base_url": "http://localhost:8080",  # lamina-llm-serve default port
        "model": "llama3.2-1b-q4_k_m",
        "timeout": 30,
        "parameters": {
            "temperature": 0.7,
            "max_tokens": 50,  # Keep short for testing
        },
    }

    try:
        # Create client instance
        print("🔧 Creating LaminaLLMClient...")
        client = get_llm_client(config)
        print(f"✅ Client created: {client.__class__.__name__}")

        # Test availability
        print("\n🔍 Checking service availability...")
        is_available = await client.is_available()
        print(f"✅ Service available: {is_available}")

        if not is_available:
            print("❌ lamina-llm-serve not available. Please start it first:")
            print("   cd ../lamina-llm-serve && uv run python -m lamina_llm_serve.server")
            return

        # Test model loading
        print("\n📂 Checking model availability...")
        model_loaded = await client.load_model()
        print(f"✅ Model available: {model_loaded}")

        if not model_loaded:
            print(f"❌ Model '{config['model']}' not available in lamina-llm-serve")
            return

        # Test chat generation (non-streaming)
        print("\n💬 Testing non-streaming chat...")
        messages = [Message(role="user", content="Hello! Please respond with just 'Hi there!'")]

        response_chunks = []
        async for chunk in client.generate(messages, stream=False):
            response_chunks.append(chunk)
            print(f"   Response: {chunk}")

        full_response = "".join(response_chunks)
        print(f"✅ Non-streaming response: {len(full_response)} characters")

        # Test chat generation (streaming)
        print("\n🌊 Testing streaming chat...")
        messages = [Message(role="user", content="Count from 1 to 3, one number per word.")]

        chunk_count = 0
        async for chunk in client.generate(messages, stream=True):
            chunk_count += 1
            print(f"   Chunk {chunk_count}: {chunk[:50]}...")  # Show first 50 chars
            if chunk_count >= 5:  # Limit output for testing
                break

        print(f"✅ Streaming response: {chunk_count} chunks received")

        # Test model info
        print("\n📋 Getting model info...")
        model_info = client.get_model_info()
        print("✅ Model info:")
        for key, value in model_info.items():
            print(f"   {key}: {value}")

        print("\n🎉 All tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


async def test_client_creation():
    """Test that the client can be created."""
    print("\n🔧 Testing client creation...")

    from lamina.llm_client import LaminaLLMClient

    # Test direct creation
    client = LaminaLLMClient({"model": "test"})
    print(f"✅ Direct creation: {client.__class__.__name__}")

    # Test via get_llm_client function
    client2 = get_llm_client({"model": "test"})
    print(f"✅ Via get_llm_client: {client2.__class__.__name__}")


if __name__ == "__main__":
    # Test creation first
    asyncio.run(test_client_creation())

    # Test actual integration
    asyncio.run(test_llamaserve_client())
