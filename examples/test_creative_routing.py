#!/usr/bin/env python3
"""Test creative routing specifically."""

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

    # Test creative routing
    message = "I need help writing a creative story about time travel"
    response = await coordinator.process_message(message)
    print(f"Message: {message}")
    print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())
