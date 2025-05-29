# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

#!/usr/bin/env python3
"""
Chat Demo - Direct Agent Chat Interface

This example demonstrates chatting with agents using the Agent Coordinator
without requiring a running server.
"""

import sys

from lamina.coordination import AgentCoordinator


class SimpleAgent:
    """Simple agent implementation for demonstration"""

    def __init__(self, name: str, description: str, personality: str = "helpful"):
        self.name = name
        self.description = description
        self.personality = personality
        self.conversation_history = []

    def chat(self, message: str, context=None):
        """Simple chat implementation with personality"""

        # Store conversation
        self.conversation_history.append({"role": "user", "content": message})

        # Generate response based on agent type
        if self.name == "assistant":
            response = self._conversational_response(message)
        elif self.name == "researcher":
            response = self._analytical_response(message)
        elif self.name == "guardian":
            response = self._security_response(message)
        else:
            response = f"I'm {self.name}, {self.description}. I received: '{message}'"

        # Store response
        self.conversation_history.append({"role": "assistant", "content": response})

        return response

    def _conversational_response(self, message: str) -> str:
        """Generate conversational response"""
        if any(word in message.lower() for word in ["hello", "hi", "hey", "greetings"]):
            return f"Hello! I'm {self.name}, your friendly assistant. How can I help you today?"
        elif any(word in message.lower() for word in ["how are you", "how do you do"]):
            return "I'm doing well, thank you for asking! I'm here and ready to help with whatever you need."
        elif any(word in message.lower() for word in ["help", "assist", "support"]):
            return "I'd be happy to help! I can assist with questions, explanations, problem-solving, and general conversation. What would you like to know about?"
        elif any(word in message.lower() for word in ["thank", "thanks"]):
            return "You're very welcome! Is there anything else I can help you with?"
        else:
            return f"That's an interesting question about '{message}'. As your assistant, I'm here to help with information, explanations, and problem-solving. Could you tell me more about what specifically you'd like help with?"

    def _analytical_response(self, message: str) -> str:
        """Generate analytical response"""
        if any(word in message.lower() for word in ["analyze", "research", "study", "examine"]):
            return f"I'll analyze this systematically. For '{message}', I would approach this by: 1) Gathering relevant data, 2) Identifying patterns and trends, 3) Drawing evidence-based conclusions. What specific aspects would you like me to focus on?"
        elif any(word in message.lower() for word in ["data", "statistics", "metrics"]):
            return f"From an analytical perspective on '{message}': I would need to examine the data sources, validate the methodology, and look for statistical significance. What data do you have available?"
        else:
            return f"Analyzing your request: '{message}'. To provide a thorough analysis, I need to understand the scope, available data, and your specific research objectives. Could you provide more details?"

    def _security_response(self, message: str) -> str:
        """Generate security-focused response"""
        if any(word in message.lower() for word in ["secure", "security", "safe", "protect"]):
            return f"Security assessment for '{message}': I would evaluate this for potential vulnerabilities, access controls, and compliance requirements. What specific security concerns do you have?"
        elif any(word in message.lower() for word in ["password", "credential", "access"]):
            return "Security reminder: Never share passwords or credentials. I can help you understand security best practices. What security guidance do you need?"
        else:
            return f"From a security perspective on '{message}': I'll evaluate potential risks and recommend protective measures. What aspects of security are you most concerned about?"


def create_agents():
    """Create demo agents with different personalities"""
    return {
        "assistant": SimpleAgent(
            "Assistant", "a friendly conversational AI assistant", "helpful and conversational"
        ),
        "researcher": SimpleAgent(
            "Researcher", "an analytical research specialist", "thorough and objective"
        ),
        "guardian": SimpleAgent(
            "Guardian", "a security and safety specialist", "protective and cautious"
        ),
    }


def interactive_chat():
    """Run interactive chat with agent coordinator"""

    print("🤖 Lamina Core Chat Demo")
    print("=" * 40)

    # Create agents and coordinator
    agents = create_agents()
    coordinator = AgentCoordinator(agents)

    print("Available agents:")
    for name, agent in agents.items():
        print(f"  🔹 {name}: {agent.description}")

    print("\nThe coordinator will automatically route your messages to the most appropriate agent.")
    print("Type 'quit', 'exit', or press Ctrl+C to exit.")
    print("Type 'stats' to see routing statistics.")
    print("=" * 40)
    print()

    try:
        while True:
            # Get user input
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n👋 Goodbye!")
                break

            if not user_input:
                continue

            # Handle special commands
            if user_input.lower() in ["quit", "exit"]:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == "stats":
                stats = coordinator.get_routing_stats()
                print("\n📊 Routing Statistics:")
                print(f"   Total requests: {stats['total_requests']}")
                print(f"   Agent usage: {stats['routing_decisions']}")
                print(f"   Constraint violations: {stats['constraint_violations']}")
                print()
                continue

            # Process message through coordinator
            print("🤔 Processing...", end=" ", flush=True)
            response = coordinator.process_message(user_input)

            # Show which agent responded (for demo purposes)
            stats = coordinator.get_routing_stats()
            last_agent = None
            if stats["routing_decisions"]:
                # Find the agent that was used most recently
                for agent_name, count in stats["routing_decisions"].items():
                    if count > 0:
                        last_agent = agent_name

            print(f"\r🤖 {last_agent or 'Agent'}: {response}")
            print()

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


def single_message_chat(agent_name: str, message: str):
    """Send a single message to a specific agent"""

    agents = create_agents()

    if agent_name not in agents:
        print(f"❌ Agent '{agent_name}' not found. Available: {list(agents.keys())}")
        return

    coordinator = AgentCoordinator(agents)
    response = coordinator.process_message(message)

    print(f"🤖 {agent_name}: {response}")


def main():
    """Main entry point"""

    if len(sys.argv) == 1:
        # Interactive mode
        interactive_chat()
    elif len(sys.argv) == 3:
        # Single message mode: python chat_demo.py <agent> "<message>"
        agent_name = sys.argv[1]
        message = sys.argv[2]
        single_message_chat(agent_name, message)
    else:
        print("Usage:")
        print("  python chat_demo.py                    # Interactive chat")
        print('  python chat_demo.py <agent> "<message>"  # Single message')
        print()
        print("Available agents: assistant, researcher, guardian")


if __name__ == "__main__":
    main()
