#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Demo: Integration between lamina-llm-serve and lamina-core

Shows how the model cache can be used by the agent system.
"""

from lamina_llm_serve.backends import list_available_backends
from lamina_llm_serve.model_manager import ModelManager


def demo_model_discovery():
    """Demonstrate model discovery and selection"""
    print("🔍 Model Discovery Demo")
    print("=" * 40)

    manager = ModelManager()

    # Show available models
    models = manager.list_models()
    print(f"📋 Available models: {len(models)}")
    for model_name in models:
        info = manager.get_model_info(model_name)
        available = "✅" if manager.is_model_available(model_name) else "❌"
        print(f"   {available} {model_name} ({info['backend']}, {info['size']})")

    # Show model suggestion for different agent types
    print("\n🎯 Model suggestions for different agent types:")

    agent_configs = [
        {"template": "conversational", "use_case": "conversational"},
        {"template": "analytical", "use_case": "analytical"},
        {"template": "security", "use_case": "security"},
        {"template": "reasoning", "use_case": "reasoning"},
    ]

    for config in agent_configs:
        suggested = manager.get_model_for_agent(config)
        print(f"   {config['template']}: {suggested or 'No model available'}")

    # Show backend availability
    print("\n🔧 Backend availability:")
    available_backends = list_available_backends(manager.backends)
    for backend_name in manager.backends:
        status = "✅" if backend_name in available_backends else "❌"
        print(f"   {status} {backend_name}")


def demo_agent_model_integration():
    """Show how agents would get models from the cache"""
    print("\n🤖 Agent-Model Integration Demo")
    print("=" * 40)

    manager = ModelManager()

    # Simulate different agent configurations
    agent_scenarios = [
        {
            "name": "assistant",
            "template": "conversational",
            "description": "General chat assistant",
        },
        {
            "name": "researcher",
            "template": "analytical",
            "ai_model": "llama3-8b-q4_k_m",  # Explicitly request specific model
            "description": "Research specialist",
        },
        {
            "name": "guardian",
            "template": "security",
            "category": "reasoning",
            "description": "Security specialist",
        },
    ]

    for agent in agent_scenarios:
        print(f"\n🎭 Agent: {agent['name']} ({agent['description']})")

        # Get suggested model
        suggested_model = manager.get_model_for_agent(agent)
        if suggested_model:
            model_info = manager.get_model_info(suggested_model)
            available = manager.is_model_available(suggested_model)

            print(f"   Suggested model: {suggested_model}")
            print(f"   Backend: {model_info['backend']}")
            print(f"   Size: {model_info['size']}")
            print(f"   Available: {'✅' if available else '❌'}")

            if not available:
                print(f"   ⚠️  Would need to download: {model_info['path']}")
        else:
            print("   ❌ No suitable model found")


def demo_server_capabilities():
    """Show server API capabilities"""
    print("\n🌐 Server API Capabilities")
    print("=" * 40)

    print("Available endpoints:")
    endpoints = [
        ("GET /health", "Server health and statistics"),
        ("GET /models", "List all available models"),
        ("GET /models/<name>", "Get specific model info"),
        ("POST /models/<name>/start", "Start model server"),
        ("POST /models/<name>/stop", "Stop model server"),
        ("GET /backends", "List available backends"),
        ("POST /suggest", "Suggest model for requirements"),
        ("POST /chat/<model>", "Proxy chat to model server"),
    ]

    for endpoint, description in endpoints:
        print(f"   {endpoint:<25} - {description}")

    print("\n💡 Usage example:")
    print("   # Start server: python -m lamina_llm_serve.server")
    print("   # List models: curl http://localhost:8080/models")
    print("   # Start model: curl -X POST http://localhost:8080/models/llama3.2-3b-q4_k_m/start")
    print(
        '   # Chat: curl -X POST http://localhost:8080/chat/llama3.2-3b-q4_k_m -d \'{"message":"Hello"}\''
    )


def main():
    """Run all demos"""
    print("🚀 Lamina LLM Serve Integration Demo")
    print("=" * 50)

    try:
        demo_model_discovery()
        demo_agent_model_integration()
        demo_server_capabilities()

        print("\n✨ Integration demo completed!")
        print("\nNext steps to set up real models:")
        print("1. Download models: ollama pull llama3.2:3b")
        print("2. Update models.yaml paths to point to actual model files")
        print("3. Install backend tools: brew install llama.cpp")
        print("4. Start server: python -m lamina_llm_serve.server")
        print("5. Test with: curl http://localhost:8080/models")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
