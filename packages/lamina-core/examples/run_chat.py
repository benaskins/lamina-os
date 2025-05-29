# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

#!/usr/bin/env python3
"""
Simple script to demonstrate interactive chat
Run this to try chatting with the agents!
"""

import os
import sys

sys.path.append(os.path.dirname(__file__))
from chat_demo import create_agents

from lamina.coordination import AgentCoordinator


def demo_chat():
    """Demo chat with predefined conversation"""

    print("🤖 Lamina Core Chat Demo")
    print("=" * 40)

    # Create agents and coordinator
    agents = create_agents()
    coordinator = AgentCoordinator(agents)

    print("Available agents:")
    for name, agent in agents.items():
        print(f"  🔹 {name}: {agent.description}")
    print()

    # Demo conversation
    demo_messages = [
        "Hello, I need help with something",
        "Can you analyze the security of my password policy?",
        "Research the best practices for AI safety",
        "Help me understand machine learning",
    ]

    for i, message in enumerate(demo_messages, 1):
        print(f"Demo Message {i}:")
        print(f"User: {message}")

        response = coordinator.process_message(message)
        print(f"System: {response}")
        print()

    # Show final stats
    stats = coordinator.get_routing_stats()
    print("📊 Final Statistics:")
    print(f"   Total requests: {stats['total_requests']}")
    print(f"   Agent usage: {stats['routing_decisions']}")
    print(f"   Constraint violations: {stats['constraint_violations']}")


if __name__ == "__main__":
    demo_chat()
