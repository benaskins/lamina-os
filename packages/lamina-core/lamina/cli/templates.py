# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Agent and Sanctuary Templates

Professional templates for scaffolding agents and sanctuaries
with clean, production-ready configurations.
"""

from typing import Any

# Agent templates for scaffolding
AGENT_TEMPLATES: dict[str, dict[str, Any]] = {
    "conversational": {
        "description": "Friendly conversational agent for general interaction and assistance",
        "ai_provider": "ollama",
        "ai_model": "llama3.2:3b",
        "ai_parameters": {"temperature": 0.7, "top_p": 0.9, "max_tokens": 2048},
        "personality_traits": ["helpful", "friendly", "clear", "patient"],
        "communication_style": "conversational",
        "expertise_areas": ["general_knowledge", "problem_solving", "assistance", "communication"],
        "memory_enabled": True,
        "memory_database": "long-term",
        "memory_embedding_model": "all-MiniLM-L6-v2",
        "functions": ["chat", "help", "explain"],
        "constraints": ["basic_safety", "privacy_protection"],
    },
    "analytical": {
        "description": "Research and analysis focused agent for data processing and insights",
        "ai_provider": "ollama",
        "ai_model": "llama3.2:3b",
        "ai_parameters": {"temperature": 0.3, "top_p": 0.8, "max_tokens": 4096},
        "personality_traits": ["analytical", "thorough", "precise", "objective"],
        "communication_style": "precise",
        "expertise_areas": [
            "research",
            "analysis",
            "data_processing",
            "pattern_recognition",
            "insights",
        ],
        "memory_enabled": True,
        "memory_database": "analytical",
        "memory_embedding_model": "all-MiniLM-L6-v2",
        "functions": ["analyze", "research", "summarize", "compare"],
        "constraints": ["basic_safety", "privacy_protection", "data_integrity"],
    },
    "security": {
        "description": "Security validation and protection agent for system safety",
        "ai_provider": "ollama",
        "ai_model": "llama3.2:3b",
        "ai_parameters": {"temperature": 0.2, "top_p": 0.7, "max_tokens": 2048},
        "personality_traits": ["vigilant", "protective", "systematic", "thorough"],
        "communication_style": "direct",
        "expertise_areas": [
            "security",
            "validation",
            "risk_assessment",
            "threat_detection",
            "compliance",
        ],
        "memory_enabled": True,
        "memory_database": "security",
        "memory_embedding_model": "all-MiniLM-L6-v2",
        "functions": ["validate", "scan", "assess_risk", "enforce_policy"],
        "constraints": ["basic_safety", "security_review", "privacy_protection", "access_control"],
    },
    "reasoning": {
        "description": "Logic and problem-solving specialist for complex reasoning tasks",
        "ai_provider": "ollama",
        "ai_model": "llama3.2:3b",
        "ai_parameters": {"temperature": 0.1, "top_p": 0.8, "max_tokens": 3072},
        "personality_traits": ["logical", "methodical", "efficient", "precise"],
        "communication_style": "concise",
        "expertise_areas": ["reasoning", "logic", "mathematics", "problem_solving", "algorithms"],
        "memory_enabled": True,
        "memory_database": "reasoning",
        "memory_embedding_model": "all-MiniLM-L6-v2",
        "functions": ["solve", "calculate", "deduce", "optimize"],
        "constraints": ["basic_safety", "logical_consistency", "accuracy_verification"],
    },
}

# Sanctuary templates for different use cases
SANCTUARY_TEMPLATES: dict[str, dict[str, Any]] = {
    "basic": {
        "description": "Basic sanctuary with essential components",
        "includes": [
            "Single conversational agent",
            "Basic infrastructure",
            "Essential constraints",
            "Docker support",
        ],
        "default_agents": ["assistant"],
        "complexity": "beginner",
    },
    "advanced": {
        "description": "Advanced sanctuary with multiple specialized agents",
        "includes": [
            "Multiple specialized agents",
            "Advanced coordination",
            "Full observability stack",
            "Custom constraint system",
            "Houses and essence system",
        ],
        "default_agents": ["assistant", "researcher", "guardian"],
        "complexity": "intermediate",
    },
    "custom": {
        "description": "Fully customizable sanctuary for expert users",
        "includes": [
            "Custom agent configurations",
            "Advanced coordination patterns",
            "Custom constraint definitions",
            "Full infrastructure control",
        ],
        "default_agents": [],
        "complexity": "advanced",
    },
}

# Infrastructure templates for different deployment scenarios
INFRASTRUCTURE_TEMPLATES: dict[str, dict[str, Any]] = {
    "local": {
        "description": "Local development setup",
        "docker_compose": True,
        "mtls": False,
        "observability": "basic",
        "storage": "local",
    },
    "production": {
        "description": "Production-ready deployment",
        "docker_compose": True,
        "mtls": True,
        "observability": "full",
        "storage": "persistent",
        "backup": True,
        "monitoring": True,
    },
    "minimal": {
        "description": "Minimal resource usage",
        "docker_compose": True,
        "mtls": False,
        "observability": "disabled",
        "storage": "memory",
    },
}

# Constraint templates for different security levels
CONSTRAINT_TEMPLATES: dict[str, dict[str, Any]] = {
    "permissive": {
        "description": "Minimal constraints for development",
        "safety_level": "basic",
        "privacy_level": "basic",
        "security_level": "basic",
    },
    "standard": {
        "description": "Balanced constraints for general use",
        "safety_level": "standard",
        "privacy_level": "standard",
        "security_level": "standard",
    },
    "strict": {
        "description": "Strict constraints for sensitive environments",
        "safety_level": "high",
        "privacy_level": "high",
        "security_level": "high",
    },
}


def get_agent_template(template_name: str) -> dict[str, Any]:
    """Get agent template by name"""
    return AGENT_TEMPLATES.get(template_name, AGENT_TEMPLATES["conversational"])


def get_sanctuary_template(template_name: str) -> dict[str, Any]:
    """Get sanctuary template by name"""
    return SANCTUARY_TEMPLATES.get(template_name, SANCTUARY_TEMPLATES["basic"])


def list_agent_templates() -> list[str]:
    """List available agent templates"""
    return list(AGENT_TEMPLATES.keys())


def list_sanctuary_templates() -> list[str]:
    """List available sanctuary templates"""
    return list(SANCTUARY_TEMPLATES.keys())


def get_template_info(template_type: str, template_name: str) -> dict[str, Any]:
    """Get detailed information about a template"""

    templates_map = {
        "agent": AGENT_TEMPLATES,
        "sanctuary": SANCTUARY_TEMPLATES,
        "infrastructure": INFRASTRUCTURE_TEMPLATES,
        "constraint": CONSTRAINT_TEMPLATES,
    }

    templates = templates_map.get(template_type, {})
    return templates.get(template_name, {})
