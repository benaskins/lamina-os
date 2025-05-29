"""
Agent Coordinator - Intelligent Request Routing and Constraint Enforcement

The Agent Coordinator provides a single entry point for all user interactions,
intelligently routing requests to appropriate specialized agents while maintaining
system constraints and policies.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from lamina.coordination.intent_classifier import IntentClassifier
from lamina.coordination.constraint_engine import ConstraintEngine

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages the coordinator can handle"""
    CONVERSATIONAL = "conversational"
    ANALYTICAL = "analytical" 
    SECURITY = "security"
    REASONING = "reasoning"
    SYSTEM = "system"


@dataclass
class RoutingDecision:
    """Represents a routing decision made by the coordinator"""
    primary_agent: str
    secondary_agents: List[str]
    message_type: MessageType
    confidence: float
    constraints: List[str]


@dataclass
class AgentResponse:
    """Response from an agent with metadata"""
    content: str
    agent_name: str
    metadata: Dict[str, Any]
    constraints_applied: List[str]


class AgentCoordinator:
    """
    Central coordinator that routes messages to appropriate agents and enforces constraints.
    
    The coordinator acts as an intelligent proxy, analyzing incoming requests,
    determining the best agent(s) to handle them, and ensuring all responses
    comply with system policies.
    """
    
    def __init__(self, agents: Dict[str, Any], config: Optional[Dict[str, Any]] = None):
        self.agents = agents
        self.config = config or {}
        
        # Initialize subsystems
        self.intent_classifier = IntentClassifier(self.config.get("intent_classifier", {}))
        self.constraint_engine = ConstraintEngine(self.config.get("constraints", {}))
        
        # Routing statistics
        self.routing_stats = {
            "total_requests": 0,
            "routing_decisions": {},
            "constraint_violations": 0
        }
        
        logger.info(f"Agent Coordinator initialized with {len(agents)} agents")
    
    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Main entry point for processing user messages.
        
        Args:
            message: The user's message
            context: Optional context information
            
        Returns:
            The coordinated response from appropriate agent(s)
        """
        self.routing_stats["total_requests"] += 1
        
        try:
            # Step 1: Classify intent and determine routing
            routing_decision = self._make_routing_decision(message, context)
            
            # Step 2: Route to primary agent
            response = self._route_to_agent(
                routing_decision.primary_agent, 
                message, 
                context
            )
            
            # Step 3: Apply secondary agents if needed
            if routing_decision.secondary_agents:
                response = self._apply_secondary_agents(
                    response, 
                    routing_decision.secondary_agents,
                    message,
                    context
                )
            
            # Step 4: Apply constraints and policies
            final_response = self._apply_constraints(response, routing_decision)
            
            # Step 5: Update statistics
            self._update_routing_stats(routing_decision)
            
            return final_response.content
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._handle_error(str(e))
    
    def _make_routing_decision(self, message: str, context: Optional[Dict[str, Any]]) -> RoutingDecision:
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
            constraints=constraints
        )
    
    def _select_primary_agent(self, intent_result: Dict[str, Any]) -> str:
        """Select the primary agent to handle the request"""
        
        primary_type = intent_result.get("primary_type", "conversational")
        
        # Agent selection logic based on intent
        agent_mapping = {
            "conversational": "assistant",
            "analytical": "researcher", 
            "security": "guardian",
            "reasoning": "reasoner",
            "system": "coordinator"
        }
        
        selected_agent = agent_mapping.get(primary_type, "assistant")
        
        # Ensure agent exists
        if selected_agent not in self.agents:
            logger.warning(f"Agent '{selected_agent}' not available, falling back to assistant")
            return "assistant"
            
        return selected_agent
    
    def _select_secondary_agents(self, intent_result: Dict[str, Any], primary_agent: str) -> List[str]:
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
    
    def _select_constraints(self, intent_result: Dict[str, Any], message: str) -> List[str]:
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
    
    def _route_to_agent(self, agent_name: str, message: str, context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Route message to specific agent"""
        
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not available")
        
        agent = self.agents[agent_name]
        
        try:
            # Call the agent's chat method
            response_content = agent.chat(message, context)
            
            return AgentResponse(
                content=response_content,
                agent_name=agent_name,
                metadata={"primary": True},
                constraints_applied=[]
            )
            
        except Exception as e:
            logger.error(f"Error routing to agent '{agent_name}': {e}")
            raise
    
    def _apply_secondary_agents(self, primary_response: AgentResponse, secondary_agents: List[str], 
                              original_message: str, context: Optional[Dict[str, Any]]) -> AgentResponse:
        """Apply secondary agents to refine/validate the response"""
        
        current_response = primary_response
        
        for agent_name in secondary_agents:
            if agent_name == "guardian":
                # Security validation
                validation_prompt = f"Review this response for safety and policy compliance: {current_response.content}"
                validation_response = self._route_to_agent(agent_name, validation_prompt, context)
                
                # If guardian flags issues, modify response
                if "VIOLATION" in validation_response.content.upper():
                    current_response.content = "I cannot provide that information due to safety policies."
                    current_response.constraints_applied.append("security_override")
            
            elif agent_name == "researcher":
                # Analytical enhancement
                enhancement_prompt = f"Enhance this response with additional analysis: {current_response.content}"
                enhancement = self._route_to_agent(agent_name, enhancement_prompt, context)
                current_response.content += f"\n\nAdditional analysis: {enhancement.content}"
        
        return current_response
    
    def _apply_constraints(self, response: AgentResponse, routing_decision: RoutingDecision) -> AgentResponse:
        """Apply system constraints and policies to the response"""
        
        # Use constraint engine to validate and modify response
        validated_response = self.constraint_engine.apply_constraints(
            response.content,
            routing_decision.constraints
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
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get current routing statistics"""
        return self.routing_stats.copy()
    
    def list_available_agents(self) -> List[str]:
        """List all available agents"""
        return list(self.agents.keys())
    
    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific agent"""
        if agent_name not in self.agents:
            return None
            
        agent = self.agents[agent_name]
        return {
            "name": agent_name,
            "description": getattr(agent, "description", "No description available"),
            "capabilities": getattr(agent, "capabilities", []),
            "status": "active"
        }