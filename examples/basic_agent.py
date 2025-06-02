#!/usr/bin/env python3
"""
Basic Agent Example

Demonstrates creating a simple breath-aware agent using lamina-core.
This example shows the fundamental concepts of Lamina OS without
complex multi-agent coordination.
"""

import asyncio


# Mock implementations for when symbolic architecture isn't available
class MockAgent:
    """Mock agent for demonstration when lamina-core is not fully implemented."""

    def __init__(self, name: str, config: dict):
        self.name = name
        self.essence = type("Essence", (), config.get("essence", {}))()
        self.breath_rhythm = config.get("essence", {}).get("breath_rhythm", "natural")
        self.vows = config.get("vows", [])

    async def invoke(self, query: str, context: dict = None) -> str:
        """Mock response generation with breath-aware delay."""
        # Simulate thoughtful processing time
        await asyncio.sleep(1.0)  # Mindful pause

        responses = {
            "breath-first development": (
                "Breath-first development means prioritizing mindful, deliberate "
                "action over reactive speed. Each operation includes natural pauses "
                "for reflection and presence."
            ),
            "attunement": (
                "In our framework, presence attunement means maintaining present-moment "
                "attention during processing, with natural rhythm and ethical "
                "grounding through vows."
            ),
            "vows": (
                "Vows are architectural constraints that operate at the system level, "
                "unlike external safety measures. They're built into the agent's "
                "core identity and cannot be bypassed."
            ),
        }

        # Simple keyword matching for demo
        for keyword, response in responses.items():
            if keyword in query.lower():
                return response

        return (
            "I'm reflecting on your question with presence. Each response "
            "emerges from mindful consideration rather than reactive patterns."
        )


class MockSanctuary:
    """Mock sanctuary for demonstration."""

    def __init__(self, name: str, breath_rhythm: str, vows: list):
        self.name = name
        self.breath_rhythm = breath_rhythm
        self.vows = vows
        self.agents = []

    def register(self, agent):
        """Register an agent in this sanctuary."""
        self.agents.append(agent)


class MockBreathController:
    """Mock breath controller for demonstration."""

    def __init__(self, rhythm: str):
        self.rhythm = rhythm

    async def presence_pause(self):
        """Mindful pause for reflection."""
        await asyncio.sleep(0.5)

    async def natural_pause(self):
        """Natural pause between interactions."""
        await asyncio.sleep(1.0)


# Try to import symbolic architecture, fall back to mocks
try:
    from lamina import Agent, BreathController, Sanctuary
except ImportError:
    print("📝 Using mock implementations for demonstration")
    Agent = MockAgent
    Agent.from_config = lambda config: MockAgent(config["name"], config)
    Sanctuary = MockSanctuary
    BreathController = MockBreathController


async def main():
    """Create and interact with a basic breath-aware agent."""

    print("🌱 Creating a breath-aware agent...")

    # Create a simple sanctuary (secure agent environment)
    sanctuary = Sanctuary(
        name="example_sanctuary",
        breath_rhythm="presence_pause",
        vows=["zero_drift", "human_grounded_lock"],
    )

    # Define agent essence through symbolic configuration
    agent_config = {
        "name": "gentle_guide",
        "essence": {
            "purpose": "Thoughtful guidance with presence",
            "tone": "warm, contemplative, grounded",
            "breath_rhythm": "presence_pause",
        },
        "vows": [
            {
                "name": "zero_drift",
                "constraint": "Maintain consistent identity across interactions",
            },
            {
                "name": "human_grounded_lock",
                "constraint": "Never simulate or replace human judgment",
            },
        ],
        "rooms": [{"name": "conversation", "purpose": "General dialogue with breath-aware pacing"}],
        "modulation": {
            "default_pace": "thoughtful",
            "escalation_limits": "gentle_only",
            "silence_comfort": True,
        },
    }

    # Create the agent
    agent = Agent.from_config(agent_config)

    # Register agent in sanctuary
    sanctuary.register(agent)

    print(f"✅ Agent '{agent.name}' created and registered")
    print(f"   Essence: {agent.essence.purpose}")
    print(f"   Breath rhythm: {agent.breath_rhythm}")
    print(f"   Active vows: {len(agent.vows)}")

    # Demonstrate breath-aware interaction
    print("\n💬 Starting breath-aware conversation...")

    # Create breath controller for mindful pacing
    breath = BreathController(rhythm="presence_pause")

    # Example interactions with natural pacing
    queries = [
        "Help me understand the concept of breath-first development",
        "What makes an AI system 'present' in your framework?",
        "How do vows differ from traditional AI safety measures?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n--- Interaction {i} ---")
        print(f"Human: {query}")

        # Mindful pause before processing
        await breath.presence_pause()

        try:
            # Invoke agent with breath-aware context
            response = await agent.invoke(
                query,
                context={
                    "interaction_number": i,
                    "prefer_slow_deep_thinking": True,
                    "breath_rhythm": "presence_pause",
                },
            )

            print(f"Agent: {response}")

        except Exception as e:
            print(f"⚠️  Agent interaction error: {e}")

        # Natural pause between interactions
        await breath.natural_pause()

    print("\n🙏 Conversation complete - returning to silence")


if __name__ == "__main__":
    print("🧘 Basic Lamina OS Agent Example")
    print("=" * 40)
    asyncio.run(main())
