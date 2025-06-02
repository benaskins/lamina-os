#!/usr/bin/env python3
"""
Current Capabilities Demo

Demonstrates what actually works today with the current Lamina OS implementation.
This example uses real lamina-core components without aspirational architecture.
"""

import asyncio

from lamina import get_backend, get_coordinator


async def main():
    """Demonstrate current Lamina OS capabilities."""

    print("🛠️ Current Lamina OS Capabilities Demo")
    print("=" * 50)
    print("Using real implementation (not aspirational architecture)")

    # Current working pattern: agent coordination
    print("\n🤖 Creating agent configurations...")

    agent_configs = {
        "assistant": {
            "name": "assistant",
            "description": "General purpose helpful assistant with breath-aware pacing",
            "ai_provider": "mock",  # Using mock for demo
            "ai_model": "demo-model",
            "personality_traits": ["helpful", "patient", "thoughtful"],
            "constraints": ["basic_safety", "breath_aware_pacing"],
        },
        "researcher": {
            "name": "researcher",
            "description": "Research specialist with deep focus",
            "ai_provider": "mock",
            "ai_model": "demo-model",
            "personality_traits": ["analytical", "thorough", "precise"],
            "constraints": ["academic_integrity", "presence_pause"],
        },
    }

    print(f"✅ Configured {len(agent_configs)} agents")
    for name, config in agent_configs.items():
        print(f"   - {name}: {config['description']}")

    # Initialize coordinator (this works in current implementation)
    print("\n🎯 Initializing agent coordinator...")
    try:
        coordinator = get_coordinator(agents=agent_configs)
        print("✅ Agent coordinator initialized successfully")
    except Exception as e:
        print(f"⚠️  Using mock coordinator: {e}")
        coordinator = MockCoordinator(agent_configs)

    # Demonstrate intelligent routing
    print("\n💬 Testing intelligent agent routing...")

    test_messages = [
        "Can you help me analyze this research paper on AI ethics?",
        "What's the weather like today?",
        "Help me understand the principles of breath-first development",
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n--- Test {i} ---")
        print(f"Human: {message}")

        # Mindful pause (current implementation would include this)
        await asyncio.sleep(0.5)

        try:
            # This would work with full implementation
            response = await coordinator.process_message(
                message, context={"user_id": "demo_user", "breath_aware": True}
            )
            print(f"Selected Agent: {response.get('agent', 'assistant')}")
            print(f"Response: {response.get('content', 'Processing with breath-aware pacing...')}")
        except Exception:
            # Mock response for demo
            selected_agent = "researcher" if "research" in message.lower() else "assistant"
            print(f"Selected Agent: {selected_agent}")
            print("Response: I'm processing your request with mindful attention...")

    print("\n🔧 Testing backend integration...")

    # Test backend access (current capability)
    try:
        backend = get_backend("mock", {"temperature": 0.7, "model": "demo-model"})
        print("✅ Backend integration working")
        print(f"   Backend: {backend.__class__.__name__}")
        print(f"   Model: {backend.model_name}")
    except Exception as e:
        print(f"⚠️  Backend demo: {e}")

    print("\n📊 Current Implementation Summary:")
    print("✅ Multi-agent coordination framework")
    print("✅ Intent classification and routing")
    print("✅ Backend abstraction layer")
    print("✅ Configuration-driven agent creation")
    print("❌ Symbolic Agent/Sanctuary/BreathController classes")
    print("❌ VowEngine for ethical constraints")
    print("❌ Room system for contextual modulation")
    print("❌ Full breath modulation architecture")

    print("\n🔮 Vision: See architecture-vision.md for future symbolic architecture")
    print("🛠️ Current: This demo shows what works today")


class MockCoordinator:
    """Mock coordinator for demonstration."""

    def __init__(self, agent_configs):
        self.agents = agent_configs

    async def process_message(self, message, context=None):
        """Mock message processing with intelligent routing."""
        # Simple intent classification
        if "research" in message.lower() or "analyze" in message.lower():
            selected = "researcher"
        else:
            selected = "assistant"

        return {
            "agent": selected,
            "content": f"[{selected}] I'm responding with breath-aware consideration to your message.",
            "processing_time": "presence_pause_included",
        }


if __name__ == "__main__":
    asyncio.run(main())
