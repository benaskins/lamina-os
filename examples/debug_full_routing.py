#!/usr/bin/env python3
"""Debug full routing logic."""

import asyncio

from lamina import get_coordinator


async def main():
    agents = {
        "creative": {
            "name": "creative",
            "description": "Creative agent for artistic tasks",
            "personality_traits": ["creative", "imaginative"],
            "expertise_areas": ["writing", "art"],
        },
        "assistant": {
            "name": "assistant",
            "description": "General assistant",
            "personality_traits": ["helpful"],
            "expertise_areas": ["general"],
        },
    }

    coordinator = get_coordinator(agents=agents)

    # Test the routing decision process manually
    message = "I need help writing a creative story about time travel"

    # Get intent classification
    intent = coordinator.intent_classifier.classify(message)
    print(f"Intent classification: {intent}")

    # Make routing decision
    routing_decision = coordinator._make_routing_decision(message, {})
    print(f"Routing decision: {routing_decision}")
    print(f"Primary agent: {routing_decision.primary_agent}")
    print(f"Available agents: {list(agents.keys())}")


if __name__ == "__main__":
    asyncio.run(main())
