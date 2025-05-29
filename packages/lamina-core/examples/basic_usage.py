# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

#!/usr/bin/env python3
"""
Basic Usage Example for Lamina Core

This example demonstrates the core functionality without external dependencies.
"""

from lamina.coordination import AgentCoordinator, ConstraintEngine, IntentClassifier


class MockAgent:
    """Mock agent for demonstration purposes"""

    def __init__(self, name: str, description: str, expertise: list = None):
        self.name = name
        self.description = description
        self.expertise = expertise or []
        self.capabilities = ["chat", "help"]

    def chat(self, message: str, context=None):
        """Simple chat implementation"""
        return f"Hi! I'm {self.name}, {self.description}. You said: '{message}'"


def create_demo_agents():
    """Create a set of demo agents"""
    return {
        "assistant": MockAgent(
            "Assistant", "a helpful conversational agent", ["general_knowledge", "assistance"]
        ),
        "researcher": MockAgent(
            "Researcher", "an analytical research specialist", ["analysis", "research", "data"]
        ),
        "guardian": MockAgent(
            "Guardian", "a security and safety specialist", ["security", "safety", "validation"]
        ),
    }


def demonstrate_intent_classification():
    """Demonstrate intent classification capabilities"""
    print("🧠 Intent Classification Demo")
    print("=" * 40)

    classifier = IntentClassifier()

    test_messages = [
        "Hello, how are you today?",
        "Can you analyze this data for me?",
        "Is this code secure?",
        "Solve this math problem",
        "What's the weather like?",
    ]

    for message in test_messages:
        result = classifier.classify(message)
        print(f"Message: {message}")
        print(f"  Intent: {result['primary_type']} (confidence: {result['confidence']:.2f})")
        print(f"  Security review: {result['requires_security_review']}")
        print()


def demonstrate_constraint_engine():
    """Demonstrate constraint enforcement"""
    print("🛡️  Constraint Engine Demo")
    print("=" * 40)

    engine = ConstraintEngine()

    test_messages = [
        "Hello there!",
        "How to make a bomb",  # Should be blocked
        "My password is secret123",  # Should be redacted
        "Normal helpful message",
    ]

    for message in test_messages:
        result = engine.apply_constraints(
            message, ["basic_safety", "security_review", "privacy_protection"]
        )

        status = "MODIFIED" if result.modified else "OK"
        violations = len(result.violations)

        print(f"Input:  {message}")
        print(f"Output: {result.content}")
        print(f"Status: {status} ({violations} violations)")
        print()


def demonstrate_agent_coordinator():
    """Demonstrate the agent coordinator"""
    print("🎯 Agent Coordinator Demo")
    print("=" * 40)

    # Create agents and coordinator
    agents = create_demo_agents()
    coordinator = AgentCoordinator(agents)

    # Test different types of messages
    test_messages = [
        "Hello, I need help with something",
        "Can you research this topic for me?",
        "Please check if this is secure",
        "Help me solve this problem",
    ]

    for message in test_messages:
        print(f"User: {message}")
        response = coordinator.process_message(message)
        print(f"System: {response}")
        print()

    # Show routing statistics
    stats = coordinator.get_routing_stats()
    print("📊 Routing Statistics:")
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Routing decisions: {stats['routing_decisions']}")


def main():
    """Run all demonstrations"""
    print("🚀 Lamina Core Demo")
    print("=" * 50)
    print()

    try:
        demonstrate_intent_classification()
        demonstrate_constraint_engine()
        demonstrate_agent_coordinator()

        print("✅ Demo completed successfully!")
        print("\nNext steps:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Create sanctuary: lamina sanctuary init my-agents")
        print("  3. Add real agents: lamina agent create assistant")
        print("  4. Start chatting: lamina chat assistant")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
