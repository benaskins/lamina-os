"""
Agent Coordination and Communication

This module handles multi-agent coordination, intent routing,
and inter-agent communication patterns through a unified coordinator.
"""

from .agent_coordinator import AgentCoordinator
from .intent_classifier import IntentClassifier
from .constraint_engine import ConstraintEngine

__all__ = ["AgentCoordinator", "IntentClassifier", "ConstraintEngine"]
