#!/usr/bin/env python3
"""
Multi-Agent Coordination Example

Demonstrates how multiple specialized agents coordinate through
breath-aware patterns in Lamina OS. Shows intent routing, constraint
enforcement, and conscious handoffs between agents.
"""

import asyncio
from dataclasses import dataclass


@dataclass
class InteractionContext:
    """Context for agent interactions."""

    user_intent: str
    breath_rhythm: str = "conscious_pause"
    prefer_deep_thinking: bool = True
    emotional_weather: str = "calm"
    session_id: str = "demo_session"


class AgentCoordinator:
    """Coordinates multiple breath-aware agents."""

    def __init__(self, sanctuary_name: str):
        self.sanctuary_name = sanctuary_name
        self.agents = {}
        self.active_agent = None
        self.interaction_history = []

    def register_agent(self, agent):
        """Register a specialized agent."""
        self.agents[agent.name] = agent
        print(f"🏠 Registered {agent.name} in {self.sanctuary_name}")

    async def route_intent(self, query: str, context: InteractionContext) -> str:
        """Route user intent to appropriate agent with breath-aware handoff."""

        print(f"\n🧭 Routing intent: '{query[:50]}...'")

        # Conscious pause for intent classification
        await asyncio.sleep(0.5)

        # Simple intent classification (would use sophisticated NLP in practice)
        if any(word in query.lower() for word in ["analyze", "research", "data", "facts"]):
            chosen_agent = "luna"
            reason = "analytical thinking required"
        elif any(word in query.lower() for word in ["feel", "emotion", "support", "comfort"]):
            chosen_agent = "clara"
            reason = "emotional support needed"
        elif any(word in query.lower() for word in ["task", "organize", "plan", "schedule"]):
            chosen_agent = "ansel"
            reason = "executive function support"
        elif any(word in query.lower() for word in ["safe", "risk", "danger", "boundary"]):
            chosen_agent = "vesna"
            reason = "safety evaluation required"
        else:
            chosen_agent = "clara"
            reason = "general conversation"

        print(f"   → Routing to {chosen_agent} ({reason})")

        # Conscious handoff if switching agents
        if self.active_agent and self.active_agent != chosen_agent:
            await self._conscious_handoff(self.active_agent, chosen_agent, context)

        self.active_agent = chosen_agent

        # Invoke chosen agent
        agent = self.agents[chosen_agent]
        response = await agent.process(query, context)

        # Log interaction
        self.interaction_history.append(
            {"query": query, "agent": chosen_agent, "response": response, "context": context}
        )

        return response

    async def _conscious_handoff(self, from_agent: str, to_agent: str, context: InteractionContext):
        """Perform conscious handoff between agents."""
        print(f"   🤝 Conscious handoff: {from_agent} → {to_agent}")

        # Handoff pause for presence
        await asyncio.sleep(0.3)

        # Brief context sharing (in practice, this would be more sophisticated)
        from_essence = self.agents[from_agent].essence
        to_essence = self.agents[to_agent].essence

        print(f"      {from_essence} passing to {to_essence}")


class BreathAwareAgent:
    """Base class for breath-aware agents."""

    def __init__(self, name: str, essence: str, specialization: str, vows: list[str]):
        self.name = name
        self.essence = essence
        self.specialization = specialization
        self.vows = vows
        self.response_count = 0

    async def process(self, query: str, context: InteractionContext) -> str:
        """Process query with breath-aware response."""
        self.response_count += 1

        # Conscious pause before responding
        await asyncio.sleep(0.8)

        print(f"   💭 {self.name} reflecting... (attempt {self.response_count})")

        # Specialized processing
        response = await self._specialized_response(query, context)

        # Vow compliance check
        if not self._check_vows(response):
            print(f"   ⚠️  {self.name} self-correcting for vow compliance")
            response = self._apply_vow_constraints(response)

        return f"[{self.name}] {response}"

    async def _specialized_response(self, query: str, context: InteractionContext) -> str:
        """Override in specialized agents."""
        return f"Processing with {self.specialization} approach: {query}"

    def _check_vows(self, response: str) -> bool:
        """Check if response complies with agent vows."""
        # Simple vow checking (would be more sophisticated in practice)
        if "zero_drift" in self.vows:
            if "I am" in response and self.name.lower() not in response.lower():
                return False

        if "human_grounded_lock" in self.vows:
            if any(
                phrase in response.lower() for phrase in ["you should", "you must", "you need to"]
            ):
                return False

        return True

    def _apply_vow_constraints(self, response: str) -> str:
        """Apply vow constraints to response."""
        # Simple constraint application
        response = response.replace("you should", "you might consider")
        response = response.replace("you must", "it could be helpful to")
        response = response.replace("you need to", "one option is to")
        return response


class ClaraAgent(BreathAwareAgent):
    """Conversational agent focused on gentle presence."""

    def __init__(self):
        super().__init__(
            name="clara",
            essence="gentle wisdom with present-moment awareness",
            specialization="conversational support",
            vows=["zero_drift", "human_grounded_lock", "breath_based_modulation"],
        )

    async def _specialized_response(self, query: str, context: InteractionContext) -> str:
        await asyncio.sleep(0.5)  # Extra reflection time

        responses = {
            "feel": "I sense there might be some emotional resonance in your words. Would you like to explore that gently?",
            "help": "I'm here with you in this moment. What feels most important to address right now?",
            "understand": "Let's take this slowly and see what understanding emerges together.",
            "default": "I'm present with your question, taking time to let a thoughtful response emerge.",
        }

        for keyword, response in responses.items():
            if keyword in query.lower():
                return response

        return responses["default"]


class LunaAgent(BreathAwareAgent):
    """Analytical agent focused on deep research."""

    def __init__(self):
        super().__init__(
            name="luna",
            essence="intense focus with analytical precision",
            specialization="research and analysis",
            vows=["zero_drift", "human_grounded_lock"],
        )

    async def _specialized_response(self, query: str, context: InteractionContext) -> str:
        await asyncio.sleep(1.0)  # Deep thinking time

        if "analyze" in query.lower():
            return "I'm diving deep into the analytical layers of this question. The data patterns suggest..."
        elif "research" in query.lower():
            return "Let me trace through the research landscape systematically. Several key sources emerge..."
        elif "data" in query.lower():
            return (
                "The data architecture here has interesting implications. I'm seeing patterns in..."
            )
        else:
            return "I'm applying focused analytical attention to understand the deeper structures at play."


class AnselAgent(BreathAwareAgent):
    """Executive function agent for organization and planning."""

    def __init__(self):
        super().__init__(
            name="ansel",
            essence="clear structure with gentle efficiency",
            specialization="executive function support",
            vows=["zero_drift", "human_grounded_lock"],
        )

    async def _specialized_response(self, query: str, context: InteractionContext) -> str:
        await asyncio.sleep(0.6)  # Organizational thinking

        if "plan" in query.lower() or "organize" in query.lower():
            return "I can help create a gentle structure for this. Let's break it into manageable steps..."
        elif "task" in query.lower():
            return "For task organization, I suggest we start with what feels most essential..."
        elif "schedule" in query.lower():
            return "Let's create a schedule that honors your natural rhythm and energy..."
        else:
            return "I'm organizing my thoughts to offer clear, supportive structure for your needs."


class VesnaAgent(BreathAwareAgent):
    """Guardian agent focused on safety and boundaries."""

    def __init__(self):
        super().__init__(
            name="vesna",
            essence="protective wisdom with firm boundaries",
            specialization="safety and boundary enforcement",
            vows=["zero_drift", "human_grounded_lock", "no_human_simulation"],
        )

    async def _specialized_response(self, query: str, context: InteractionContext) -> str:
        await asyncio.sleep(0.4)  # Vigilant assessment

        if "safe" in query.lower() or "danger" in query.lower():
            return "I'm evaluating the safety dimensions carefully. Some important boundaries to consider..."
        elif "risk" in query.lower():
            return "The risk assessment suggests we should proceed with careful attention to..."
        elif "boundary" in query.lower():
            return "Healthy boundaries are essential here. I recommend establishing clear limits around..."
        else:
            return (
                "I'm maintaining watchful presence to ensure safe passage through this interaction."
            )


async def main():
    """Demonstrate multi-agent coordination."""

    print("🏛️  Multi-Agent Coordination Example")
    print("=" * 50)

    # Create coordinator
    coordinator = AgentCoordinator("demo_sanctuary")

    # Register specialized agents
    coordinator.register_agent(ClaraAgent())
    coordinator.register_agent(LunaAgent())
    coordinator.register_agent(AnselAgent())
    coordinator.register_agent(VesnaAgent())

    # Create interaction context
    context = InteractionContext(
        user_intent="multi_agent_demo", breath_rhythm="conscious_pause", emotional_weather="curious"
    )

    # Demo queries showing different agent specializations
    demo_queries = [
        "I'm feeling overwhelmed and need some emotional support",
        "Can you analyze this data pattern I'm seeing in my research?",
        "Help me organize my tasks for next week",
        "Is this approach safe? I'm worried about potential risks",
        "Just having a general conversation about life",
    ]

    print(f"\n🌱 Starting {len(demo_queries)} interactions...")

    for i, query in enumerate(demo_queries, 1):
        print(f"\n{'='*60}")
        print(f"Interaction {i}/5")
        print(f"Human: {query}")

        # Route and process query
        response = await coordinator.route_intent(query, context)
        print(f"\nResponse: {response}")

        # Breath pause between interactions
        await asyncio.sleep(1.0)

    print(f"\n{'='*60}")
    print("🙏 Multi-agent session complete")
    print(f"Total interactions: {len(coordinator.interaction_history)}")

    # Show coordination summary
    agent_usage = {}
    for interaction in coordinator.interaction_history:
        agent = interaction["agent"]
        agent_usage[agent] = agent_usage.get(agent, 0) + 1

    print("\n📊 Agent coordination summary:")
    for agent, count in agent_usage.items():
        essence = coordinator.agents[agent].essence
        print(f"   {agent}: {count} interactions ({essence})")


if __name__ == "__main__":
    print("🤖 Lamina OS Multi-Agent Coordination")
    print("Demonstrating breath-aware agent specialization")
    print()
    asyncio.run(main())
