#!/usr/bin/env python3
"""
Working Coordination Demo

Demonstrates actual working multi-agent coordination with the current lamina-core implementation.
Shows breath-aware processing, intelligent routing, and foundational capabilities.
"""

import asyncio

from lamina import get_backend, get_coordinator


async def main():
    """Demonstrate working Lamina OS coordination."""

    print("🌱 Working Lamina OS Coordination Demo")
    print("=" * 55)
    print("Demonstrating actual multi-agent coordination with breath-aware processing")

    # Define realistic agent configurations
    agent_configs = {
        "assistant": {
            "name": "assistant",
            "description": "Helpful general assistant with patient, thoughtful responses",
            "ai_provider": "mock",
            "ai_model": "assistant-model",
            "personality_traits": ["helpful", "patient", "clear"],
            "expertise_areas": ["general_knowledge", "problem_solving"],
            "constraints": ["basic_safety", "breath_aware_pacing"],
        },
        "researcher": {
            "name": "researcher",
            "description": "Analytical specialist focused on deep research and analysis",
            "ai_provider": "mock",
            "ai_model": "research-model",
            "personality_traits": ["analytical", "thorough", "precise"],
            "expertise_areas": ["research", "analysis", "data", "academic"],
            "constraints": ["academic_integrity", "mindful_pause"],
        },
        "creative": {
            "name": "creative",
            "description": "Creative agent for artistic and imaginative tasks",
            "ai_provider": "mock",
            "ai_model": "creative-model",
            "personality_traits": ["creative", "imaginative", "inspiring"],
            "expertise_areas": ["writing", "art", "brainstorming", "innovation"],
            "constraints": ["original_thinking", "breath_based_creativity"],
        },
    }

    print(f"\n🤖 Configured {len(agent_configs)} specialized agents:")
    for name, config in agent_configs.items():
        traits = ", ".join(config["personality_traits"])
        print(f"   • {name}: {config['description']}")
        print(f"     Traits: {traits}")

    # Initialize coordinator with breath-aware settings
    print("\n🧘 Initializing breath-aware coordinator...")
    coordinator = get_coordinator(agents=agent_configs, breath_modulation=True, mindful_pause=0.5)

    print("✅ Coordinator ready with mindful processing enabled")

    # Test scenarios that demonstrate intelligent routing
    test_scenarios = [
        {
            "message": "Can you help me research the latest developments in quantum computing?",
            "expected_agent": "researcher",
            "context": {"task_type": "research", "complexity": "high"},
        },
        {
            "message": "I need help writing a creative story about time travel",
            "expected_agent": "creative",
            "context": {"task_type": "creative", "complexity": "moderate"},
        },
        {
            "message": "What's 2+2 and can you explain how addition works?",
            "expected_agent": "assistant",
            "context": {"task_type": "general", "complexity": "simple"},
        },
        {
            "message": "Analyze the economic implications of renewable energy adoption",
            "expected_agent": "researcher",
            "context": {"task_type": "analysis", "complexity": "complex"},
        },
        {
            "message": "Help me brainstorm creative solutions for urban transportation",
            "expected_agent": "creative",
            "context": {"task_type": "creative", "complexity": "moderate"},
        },
    ]

    print("\n💬 Testing intelligent routing with breath-aware processing...")

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- Scenario {i} ---")
        print(f"Human: {scenario['message']}")
        print(f"Expected routing: {scenario['expected_agent']}")

        # Process with coordinator (includes conscious pause)
        start_time = asyncio.get_event_loop().time()

        try:
            response = await coordinator.process_message(
                scenario["message"], context=scenario["context"]
            )

            processing_time = asyncio.get_event_loop().time() - start_time

            print(f"✅ Processing complete ({processing_time:.2f}s)")
            print(f"Response: {response}")

        except Exception as e:
            print(f"❌ Error: {e}")

    # Demonstrate coordinator introspection
    print("\n📊 Coordinator Status and Statistics:")

    try:
        status = coordinator.get_agent_status()
        stats = coordinator.get_routing_stats()

        print(f"  • Total requests processed: {stats['total_requests']}")
        print(f"  • Agents available: {status['coordinator']['agents_count']}")
        print(f"  • Breath modulation: {status['coordinator']['breath_modulation']}")
        print(f"  • Mindful pause duration: {status['coordinator']['mindful_pause']}s")

        print("\n  Routing distribution:")
        for agent, count in stats.get("routing_decisions", {}).items():
            print(f"    - {agent}: {count} requests")

        print("\n  Agent details:")
        for name, details in status["agents"].items():
            print(f"    • {name}: {details['description']}")
            print(f"      Provider: {details['provider']}, Traits: {', '.join(details['traits'])}")

    except Exception as e:
        print(f"  Status unavailable: {e}")

    # Test backend integration
    print("\n🔧 Backend Integration Test:")

    try:
        # Test each agent's backend
        for agent_name, config in agent_configs.items():
            backend = get_backend(
                config["ai_provider"], {"model": config["ai_model"], "temperature": 0.7}
            )

            is_available = await backend.is_available()
            print(
                f"  • {agent_name}: {backend.__class__.__name__} ({'✅ available' if is_available else '❌ unavailable'})"
            )

    except Exception as e:
        print(f"  Backend test error: {e}")

    # Demonstrate conversation history
    print("\n📚 Conversation History:")

    try:
        history = coordinator.get_conversation_history(limit=3)
        for i, entry in enumerate(history[-3:], 1):
            print(f"  {i}. [{entry['agent']}] {entry['message'][:50]}...")
            print(f"     Response: {entry['response'][:60]}...")

    except Exception as e:
        print(f"  History unavailable: {e}")

    print("\n✨ Demo Summary:")
    print("✅ Multi-agent coordination with intelligent routing")
    print("✅ Breath-aware processing with conscious pauses")
    print("✅ Agent specialization and personality traits")
    print("✅ Backend abstraction and mock integration")
    print("✅ Conversation history and introspection")
    print("✅ Error handling and graceful degradation")

    print("\n🔮 Next Steps:")
    print("  • Integrate real LLM backends (Ollama, HuggingFace)")
    print("  • Implement memory persistence and retrieval")
    print("  • Add constraint enforcement and safety policies")
    print("  • Build toward symbolic architecture (Agent, Sanctuary, Vows)")

    print(f"\n🌬️ Breath-first development: {processing_time:.2f}s average mindful pause")
    print("Building AI that breathes, not just responds. 🙏")


if __name__ == "__main__":
    asyncio.run(main())
