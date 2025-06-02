# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Intent Router for Aurelia Coordinator

Analyzes user messages to determine routing to appropriate agents.
Implements natural language intent recognition and multi-agent coordination.
"""

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RoutingDecision:
    """Represents a routing decision made by the intent router."""

    target_agents: list[str]
    confidence: float
    reasoning: str
    multi_agent: bool = False
    transparency_info: str | None = None


class IntentRouter:
    """
    Routes user messages to appropriate agents based on intent analysis.

    Implements Clara's suggested routing patterns and natural language understanding.
    """

    def __init__(self, agent_config: dict):
        self.agent_config = agent_config
        self.transparency_mode = False

        # Agent patterns from configuration
        self.agent_patterns = {
            "clara": {
                "keywords": [
                    "breath",
                    "presence",
                    "mindfulness",
                    "clara",
                    "meditation",
                    "attunement",
                ],
                "domains": [
                    "meditation",
                    "breathing",
                    "presence",
                    "attunement",
                    "general",
                ],
            },
            "luna": {
                "keywords": [
                    "fire",
                    "symbolic",
                    "creative",
                    "luna",
                    "analysis",
                    "art",
                    "symbol",
                ],
                "domains": [
                    "creativity",
                    "symbolism",
                    "analysis",
                    "research",
                    "artistic",
                ],
            },
            "phi": {
                "keywords": [
                    "philosophy",
                    "ethics",
                    "reasoning",
                    "phi",
                    "logic",
                    "moral",
                    "ethical",
                ],
                "domains": ["philosophy", "ethics", "logic", "reasoning", "moral"],
            },
        }

        # Multi-agent triggers
        self.multi_agent_triggers = [
            "what do you all think",
            "bring everyone in",
            "get all perspectives",
            "multi-agent",
            "collective wisdom",
            "everyone",
            "all agents",
        ]

        # Agent summoning patterns
        self.summoning_patterns = [
            r"bring (\w+) into this",
            r"ask (\w+) about",
            r"get (\w+)\'s perspective",
            r"include (\w+)",
            r"(\w+) join us",
        ]

    def route_message(self, message: str, context: dict | None = None) -> RoutingDecision:
        """
        Analyze message and determine routing decision.

        Args:
            message: User message to analyze
            context: Optional conversation context

        Returns:
            RoutingDecision with target agents and reasoning
        """
        message_lower = message.lower()

        # Check for transparency commands
        if "route trace on" in message_lower:
            self.transparency_mode = True
            return RoutingDecision(
                target_agents=["aurelia"],
                confidence=1.0,
                reasoning="Enabling routing transparency mode",
                transparency_info="Route tracing enabled",
            )

        if "route trace off" in message_lower:
            self.transparency_mode = False
            return RoutingDecision(
                target_agents=["aurelia"],
                confidence=1.0,
                reasoning="Disabling routing transparency mode",
                transparency_info="Route tracing disabled",
            )

        # Check for multi-agent triggers
        if self._is_multi_agent_request(message_lower):
            return RoutingDecision(
                target_agents=["clara", "luna", "phi"],
                confidence=0.9,
                reasoning="Multi-agent consultation requested",
                multi_agent=True,
                transparency_info=(
                    "Triggered by multi-agent keywords" if self.transparency_mode else None
                ),
            )

        # Check for agent summoning
        summoned_agent = self._check_agent_summoning(message_lower)
        if summoned_agent:
            return RoutingDecision(
                target_agents=[summoned_agent],
                confidence=0.95,
                reasoning=f"Explicit agent summoning: {summoned_agent}",
                transparency_info=(
                    "Direct agent reference detected" if self.transparency_mode else None
                ),
            )

        # Analyze intent for single agent routing
        agent_scores = self._calculate_agent_scores(message_lower)

        # Find best match
        best_agent = max(agent_scores.items(), key=lambda x: x[1])

        if best_agent[1] > 0.6:  # High confidence threshold
            return RoutingDecision(
                target_agents=[best_agent[0]],
                confidence=best_agent[1],
                reasoning=f"Intent analysis suggests {best_agent[0]} (score: {best_agent[1]:.2f})",
                transparency_info=(
                    self._get_transparency_info(agent_scores) if self.transparency_mode else None
                ),
            )

        # Default to Clara for general conversation
        return RoutingDecision(
            target_agents=["clara"],
            confidence=0.5,
            reasoning="Default routing to Clara for general conversation",
            transparency_info=(
                "No strong intent match, using fallback" if self.transparency_mode else None
            ),
        )

    def _is_multi_agent_request(self, message: str) -> bool:
        """Check if message requests multi-agent consultation."""
        return any(trigger in message for trigger in self.multi_agent_triggers)

    def _check_agent_summoning(self, message: str) -> str | None:
        """Check for explicit agent summoning patterns."""
        for pattern in self.summoning_patterns:
            match = re.search(pattern, message)
            if match:
                agent_name = match.group(1).lower()
                if agent_name in self.agent_patterns:
                    return agent_name
        return None

    def _calculate_agent_scores(self, message: str) -> dict[str, float]:
        """Calculate relevance scores for each agent."""
        scores = {}

        for agent, patterns in self.agent_patterns.items():
            score = 0.0

            # Keyword matching
            keyword_matches = sum(1 for keyword in patterns["keywords"] if keyword in message)
            score += keyword_matches * 0.3

            # Domain relevance (simple heuristic)
            domain_matches = sum(1 for domain in patterns["domains"] if domain in message)
            score += domain_matches * 0.4

            # Agent name bonus
            if agent in message:
                score += 0.5

            scores[agent] = min(score, 1.0)  # Cap at 1.0

        return scores

    def _get_transparency_info(self, scores: dict[str, float]) -> str:
        """Generate transparency information for routing decision."""
        score_info = ", ".join([f"{agent}: {score:.2f}" for agent, score in scores.items()])
        return f"Agent scores: {score_info}"

    def toggle_transparency(self) -> bool:
        """Toggle transparency mode and return new state."""
        self.transparency_mode = not self.transparency_mode
        return self.transparency_mode
