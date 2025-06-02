# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Agent Coordinator - Intelligent Request Routing and Constraint Enforcement

The Agent Coordinator provides a single entry point for all user interactions,
intelligently routing requests to appropriate specialized agents while maintaining
system constraints and policies.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from lamina.coordination.constraint_engine import ConstraintEngine

logger = logging.getLogger(__name__)


class MockIntentClassifier:
    """Mock intent classifier for when real one isn't available."""

    def classify(self, message: str, context: dict = None):
        """Simple intent classification based on keywords."""
        message_lower = message.lower()

        if any(word in message_lower for word in ["research", "analyze", "study", "investigate"]):
            return {
                "primary_type": "analytical",
                "confidence": 0.8,
                "categories": ["research"],
                "secondary_types": [],
            }
        elif any(
            word in message_lower
            for word in ["create", "write", "design", "imagine", "brainstorm", "creative", "story"]
        ):
            return {
                "primary_type": "creative",
                "confidence": 0.7,
                "categories": ["creative"],
                "secondary_types": [],
            }
        else:
            return {
                "primary_type": "conversational",
                "confidence": 0.6,
                "categories": ["general"],
                "secondary_types": [],
            }


class MockConstraintEngine:
    """Mock constraint engine for when real one isn't available."""

    def apply_constraints(self, content: str, constraints: list):
        """Mock constraint application."""
        return type(
            "obj", (object,), {"content": content, "modified": False, "applied_constraints": []}
        )


class MessageType(Enum):
    """Types of messages the coordinator can handle"""

    CONVERSATIONAL = "conversational"
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    SECURITY = "security"
    REASONING = "reasoning"
    SYSTEM = "system"


@dataclass
class RoutingDecision:
    """Represents a routing decision made by the coordinator"""

    primary_agent: str
    secondary_agents: list[str]
    message_type: MessageType
    confidence: float
    constraints: list[str]


@dataclass
class AgentResponse:
    """Response from an agent with metadata"""

    content: str
    agent_name: str
    metadata: dict[str, Any]
    constraints_applied: list[str]


class AgentCoordinator:
    """
    Central coordinator that routes messages to appropriate agents and enforces constraints.

    The coordinator acts as an intelligent proxy, analyzing incoming requests,
    determining the best agent(s) to handle them, and ensuring all responses
    comply with system policies.
    """

    def __init__(
        self, agents: dict[str, Any] = None, config: dict[str, Any] | None = None, **kwargs
    ):
        self.agents = agents or {}
        self.config = config or {}

        # Breath-aware settings from kwargs
        self.breath_modulation = kwargs.get("breath_modulation", True)
        self.presence_pause = kwargs.get("presence_pause", 0.5)

        # Initialize subsystems (with mock implementations for now)
        # Use MockIntentClassifier which supports creative routing
        self.intent_classifier = MockIntentClassifier()

        try:
            self.constraint_engine = ConstraintEngine(self.config.get("constraints", {}))
        except Exception:
            self.constraint_engine = MockConstraintEngine()

        # Routing statistics
        self.routing_stats = {
            "total_requests": 0,
            "routing_decisions": {},
            "constraint_violations": 0,
        }

        logger.info(f"Agent Coordinator initialized with {len(self.agents)} agents")

    async def process_message(self, message: str, context: dict[str, Any] | None = None) -> str:
        """
        Main entry point for processing user messages.

        Args:
            message: The user's message
            context: Optional context information

        Returns:
            The coordinated response from appropriate agent(s)
        """
        self.routing_stats["total_requests"] += 1

        # Mindful pause for consideration
        if self.breath_modulation:
            import asyncio

            await asyncio.sleep(self.presence_pause)

        try:
            # Step 1: Classify intent and determine routing
            routing_decision = self._make_routing_decision(message, context)

            # Step 2: Route to primary agent
            response = await self._route_to_agent(routing_decision.primary_agent, message, context)

            # Step 3: Apply secondary agents if needed
            if routing_decision.secondary_agents:
                response = await self._apply_secondary_agents(
                    response, routing_decision.secondary_agents, message, context
                )

            # Step 4: Apply constraints and policies
            final_response = self._apply_constraints(response, routing_decision)

            # Step 5: Update statistics
            self._update_routing_stats(routing_decision)

            return final_response.content

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._handle_error(str(e))

    def _make_routing_decision(
        self, message: str, context: dict[str, Any] | None
    ) -> RoutingDecision:
        """Analyze message and determine routing strategy"""

        # Classify the intent
        intent_result = self.intent_classifier.classify(message, context)

        # Determine primary agent based on intent
        primary_agent = self._select_primary_agent(intent_result)

        # Determine if secondary agents needed
        secondary_agents = self._select_secondary_agents(intent_result, primary_agent)

        # Determine constraints to apply
        constraints = self._select_constraints(intent_result, message)

        return RoutingDecision(
            primary_agent=primary_agent,
            secondary_agents=secondary_agents,
            message_type=MessageType(intent_result.get("primary_type", "conversational")),
            confidence=intent_result.get("confidence", 0.5),
            constraints=constraints,
        )

    def _select_primary_agent(self, intent_result: dict[str, Any]) -> str:
        """Select the primary agent to handle the request"""

        primary_type = intent_result.get("primary_type", "conversational")

        # Agent selection logic based on intent
        agent_mapping = {
            "conversational": "assistant",
            "analytical": "researcher",
            "creative": "creative",
            "security": "guardian",
            "reasoning": "reasoner",
            "system": "coordinator",
        }

        selected_agent = agent_mapping.get(primary_type, "assistant")

        # Ensure agent exists
        if selected_agent not in self.agents:
            logger.warning(f"Agent '{selected_agent}' not available, falling back to assistant")
            # Try to find any available agent as fallback
            available_agents = list(self.agents.keys())
            if available_agents:
                fallback = available_agents[0]
                logger.info(f"Using fallback agent: {fallback}")
                return fallback
            return "assistant"

        logger.info(f"Selected agent: {selected_agent} for intent: {primary_type}")
        return selected_agent

    def _select_secondary_agents(
        self, intent_result: dict[str, Any], primary_agent: str
    ) -> list[str]:
        """Determine if secondary agents should be involved"""

        secondary_agents = []
        secondary_types = intent_result.get("secondary_types", [])

        for secondary_type in secondary_types:
            if secondary_type == "security" and primary_agent != "guardian":
                secondary_agents.append("guardian")
            elif secondary_type == "analytical" and primary_agent != "researcher":
                secondary_agents.append("researcher")

        # Remove agents that don't exist
        return [agent for agent in secondary_agents if agent in self.agents]

    def _select_constraints(self, intent_result: dict[str, Any], message: str) -> list[str]:
        """Determine which constraints should be applied"""

        constraints = ["basic_safety"]  # Always apply basic safety

        # Add specific constraints based on intent
        if intent_result.get("requires_security_review"):
            constraints.append("security_review")

        if intent_result.get("involves_personal_data"):
            constraints.append("privacy_protection")

        if "code" in intent_result.get("categories", []):
            constraints.append("code_safety")

        return constraints

    async def _route_to_agent(
        self, agent_name: str, message: str, context: dict[str, Any] | None
    ) -> AgentResponse:
        """Route message to specific agent"""

        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not available")

        agent_config = self.agents[agent_name]

        try:
            # Mock response generation based on agent configuration
            # In full implementation, this would call actual backends
            import asyncio

            await asyncio.sleep(0.3)  # Mindful pause

            personality = agent_config.get("personality_traits", [])
            description = agent_config.get("description", "")

            # Build response based on agent traits
            if "creative" in personality:
                prefix = "This is an exciting creative challenge!"
            elif "analytical" in personality:
                prefix = "Let me analyze this carefully."
            elif "helpful" in personality:
                prefix = "I'm happy to help with that."
            else:
                prefix = "I understand your request."

            response_content = f"{prefix} [{agent_name}] {description} Processing: '{message[:50]}{'...' if len(message) > 50 else ''}'"

            return AgentResponse(
                content=response_content,
                agent_name=agent_name,
                metadata={"primary": True, "mock": True},
                constraints_applied=[],
            )

        except Exception as e:
            logger.error(f"Error routing to agent '{agent_name}': {e}")
            raise

    async def _apply_secondary_agents(
        self,
        primary_response: AgentResponse,
        secondary_agents: list[str],
        original_message: str,
        context: dict[str, Any] | None,
    ) -> AgentResponse:
        """Apply secondary agents to refine/validate the response"""

        current_response = primary_response

        for agent_name in secondary_agents:
            if agent_name == "guardian":
                # Security validation
                validation_prompt = f"Review this response for safety and policy compliance: {current_response.content}"
                validation_response = await self._route_to_agent(
                    agent_name, validation_prompt, context
                )

                # If guardian flags issues, modify response
                if "VIOLATION" in validation_response.content.upper():
                    current_response.content = (
                        "I cannot provide that information due to safety policies."
                    )
                    current_response.constraints_applied.append("security_override")

            elif agent_name == "researcher":
                # Analytical enhancement
                enhancement_prompt = (
                    f"Enhance this response with additional analysis: {current_response.content}"
                )
                enhancement = await self._route_to_agent(agent_name, enhancement_prompt, context)
                current_response.content += f"\n\nAdditional analysis: {enhancement.content}"

        return current_response

    def _apply_constraints(
        self, response: AgentResponse, routing_decision: RoutingDecision
    ) -> AgentResponse:
        """Apply system constraints and policies to the response"""

        # Use constraint engine to validate and modify response
        validated_response = self.constraint_engine.apply_constraints(
            response.content, routing_decision.constraints
        )

        if validated_response.modified:
            self.routing_stats["constraint_violations"] += 1
            response.constraints_applied.extend(validated_response.applied_constraints)
            response.content = validated_response.content

        return response

    def _update_routing_stats(self, routing_decision: RoutingDecision):
        """Update routing statistics"""
        agent_key = routing_decision.primary_agent
        if agent_key not in self.routing_stats["routing_decisions"]:
            self.routing_stats["routing_decisions"][agent_key] = 0
        self.routing_stats["routing_decisions"][agent_key] += 1

    def _handle_error(self, error_message: str) -> str:
        """Handle errors gracefully"""
        logger.error(f"Coordinator error: {error_message}")
        return "I apologize, but I encountered an error processing your request. Please try again."

    def get_routing_stats(self) -> dict[str, Any]:
        """Get current routing statistics"""
        return self.routing_stats.copy()

    def list_available_agents(self) -> list[str]:
        """List all available agents"""
        return list(self.agents.keys())

    def get_agent_info(self, agent_name: str) -> dict[str, Any] | None:
        """Get information about a specific agent"""
        if agent_name not in self.agents:
            return None

        agent_config = self.agents[agent_name]
        return {
            "name": agent_name,
            "description": agent_config.get("description", "No description available"),
            "capabilities": agent_config.get("expertise_areas", []),
            "status": "active",
        }

    def get_agent_status(self) -> dict[str, Any]:
        """Get coordinator and agent status information."""
        return {
            "coordinator": {
                "agents_count": len(self.agents),
                "conversation_count": 0,  # Would track in full implementation
                "breath_modulation": self.breath_modulation,
                "presence_pause": self.presence_pause,
            },
            "agents": {
                name: {
                    "description": config.get("description", ""),
                    "traits": config.get("personality_traits", []),
                    "provider": config.get("ai_provider", "unknown"),
                }
                for name, config in self.agents.items()
            },
        }

    def get_conversation_history(self, limit: int = 10) -> list[dict]:
        """Get recent conversation history."""
        # Mock implementation - would track real history in full version
        return []
