# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Agent Configuration Loader for Lamina OS

This module provides agent-specific configuration management with support for
multiple AI backends, parameter normalization, and provider abstraction.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Agent configuration data class"""

    name: str
    description: str = ""

    # AI Backend configuration
    ai_provider: str = "ollama"
    ai_model: str = "llama3.2:3b"
    ai_parameters: dict[str, Any] = field(default_factory=dict)
    ai_provider_config: dict[str, Any] = field(default_factory=dict)

    # Memory configuration
    memory_enabled: bool = True
    memory_database: str = "long-term"
    memory_embedding_model: str = "all-MiniLM-L6-v2"
    memory_evolution_threshold: int = 5

    # Personality configuration
    personality_traits: list[str] = field(default_factory=list)
    communication_style: str = "elegant"
    expertise_areas: list[str] = field(default_factory=list)

    # Capabilities
    functions: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    integrations: list[str] = field(default_factory=list)

    # Constraints
    max_tokens: int = 4096
    timeout_seconds: int = 30
    rate_limits: dict[str, int] = field(default_factory=dict)


class AgentConfigLoader:
    """Loads and manages agent configurations with backend abstraction"""

    def __init__(self, config_dir: str | None = None, sanctuary_path: str | None = None):
        self.config_dir = Path(config_dir or "config")
        self.sanctuary_path = Path(sanctuary_path or "sanctuary")
        self.agents_config_path = self.config_dir / "agents.yaml"
        self.environment = os.getenv("LAMINA_ENV", "development")

        self._agents_schema: dict[str, Any] | None = None
        self._provider_configs: dict[str, Any] | None = None
        self._model_mappings: dict[str, Any] | None = None
        self._parameter_mappings: dict[str, Any] | None = None

    def load_agent_schema(self) -> dict[str, Any]:
        """Load agent configuration schema and provider information"""
        if self._agents_schema is not None:
            return self._agents_schema

        try:
            if not self.agents_config_path.exists():
                logger.warning(
                    f"Agents config not found at {self.agents_config_path}, using defaults"
                )
                self._agents_schema = self._get_default_schema()
            else:
                with open(self.agents_config_path) as f:
                    self._agents_schema = yaml.safe_load(f) or {}

            # Apply environment variable substitution
            self._agents_schema = self._substitute_env_vars(self._agents_schema)

            # Cache provider configurations
            self._provider_configs = self._agents_schema.get("providers", {})
            self._model_mappings = self._agents_schema.get("model_mappings", {})
            self._parameter_mappings = self._agents_schema.get("parameter_mappings", {})

            logger.info("Loaded agent configuration schema")
            return self._agents_schema

        except Exception as e:
            logger.error(f"Failed to load agent schema: {e}")
            self._agents_schema = self._get_default_schema()
            return self._agents_schema

    def load_agent_config(self, agent_name: str) -> AgentConfig:
        """Load configuration for a specific agent"""
        try:
            # Load from sanctuary if exists
            agent_config_path = self.sanctuary_path / "agents" / agent_name / "agent.yaml"

            if agent_config_path.exists():
                with open(agent_config_path) as f:
                    agent_data = yaml.safe_load(f) or {}
            else:
                logger.info(f"Agent config not found for {agent_name}, using defaults")
                agent_data = {}

            # Apply environment variable substitution
            agent_data = self._substitute_env_vars(agent_data)

            # Apply environment-specific overrides
            agent_data = self._apply_environment_overrides(agent_data)

            # Create AgentConfig instance
            config = self._create_agent_config(agent_name, agent_data)

            # Normalize AI backend configuration
            config = self._normalize_ai_backend(config)

            logger.info(f"Loaded configuration for agent: {agent_name}")
            return config

        except Exception as e:
            logger.error(f"Failed to load agent config for {agent_name}: {e}")
            # Return default configuration
            return self._create_default_agent_config(agent_name)

    def get_provider_config(self, provider: str) -> dict[str, Any]:
        """Get configuration for a specific AI provider"""
        self.load_agent_schema()
        return self._provider_configs.get(provider, {})

    def get_model_mapping(self, standard_model: str, provider: str) -> str:
        """Get provider-specific model name from standard model name"""
        self.load_agent_schema()
        model_map = self._model_mappings.get(standard_model, {})
        return model_map.get(provider, standard_model)

    def normalize_parameters(self, parameters: dict[str, Any], provider: str) -> dict[str, Any]:
        """Normalize parameters for a specific provider"""
        self.load_agent_schema()
        normalized = {}

        for param_name, param_value in parameters.items():
            # Get provider-specific parameter name
            param_mapping = self._parameter_mappings.get(param_name, {})
            provider_param = param_mapping.get(provider, param_name)
            normalized[provider_param] = param_value

        return normalized

    def build_provider_url(self, provider: str, endpoint: str = "") -> str:
        """Build URL for a provider endpoint"""
        # Try to use infrastructure configuration first (for containerized environments)
        try:
            from lamina.infrastructure_config import get_infrastructure_config

            infra_config = get_infrastructure_config()

            # Map provider names to infrastructure service names
            service_mapping = {"ollama": "ollama", "loki": "loki", "grafana": "grafana"}

            service_name = service_mapping.get(provider)
            if service_name and endpoint:
                # Use infrastructure config for service endpoint URLs
                return infra_config.get_service_endpoint_url(service_name, endpoint)
            elif service_name:
                # Use infrastructure config for base service URLs
                return infra_config.get_service_url(service_name)

        except Exception as e:
            # Fall back to agent config if infrastructure config fails
            logger.debug(
                f"Infrastructure config unavailable for {provider}, using agent config: {e}"
            )

        # Fallback to agent configuration
        provider_config = self.get_provider_config(provider)
        base_url = provider_config.get("base_url", "")

        if endpoint and "endpoints" in provider_config:
            endpoint_path = provider_config["endpoints"].get(endpoint, "")
            return f"{base_url}{endpoint_path}"

        return base_url

    def _substitute_env_vars(self, config: dict[str, Any]) -> dict[str, Any]:
        """Recursively substitute environment variables in configuration"""
        if isinstance(config, dict):
            return {k: self._substitute_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._substitute_env_vars(item) for item in config]
        elif isinstance(config, str):
            return self._substitute_env_var_string(config)
        else:
            return config

    def _substitute_env_var_string(self, value: str) -> str:
        """Substitute environment variables in a string value"""
        import re

        # Pattern: ${VAR_NAME:-default_value} or ${VAR_NAME}
        pattern = r"\$\{([^}]+)\}"

        def replace_var(match):
            var_expr = match.group(1)
            if ":-" in var_expr:
                var_name, default_value = var_expr.split(":-", 1)
                return os.getenv(var_name.strip(), default_value.strip())
            else:
                var_name = var_expr.strip()
                env_value = os.getenv(var_name)
                if env_value is None:
                    logger.warning(
                        f"Environment variable {var_name} not found, keeping placeholder"
                    )
                    return match.group(0)  # Keep original placeholder
                return env_value

        return re.sub(pattern, replace_var, value)

    def _apply_environment_overrides(self, agent_data: dict[str, Any]) -> dict[str, Any]:
        """Apply environment-specific overrides to agent configuration"""
        self.load_agent_schema()
        environments = self._agents_schema.get("environments", {})
        env_config = environments.get(self.environment, {})
        default_overrides = env_config.get("default_overrides", {})

        if default_overrides:
            logger.debug(f"Applying {self.environment} environment overrides to agent")
            agent_data = self._deep_merge(agent_data, default_overrides)

        return agent_data

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _create_agent_config(self, agent_name: str, agent_data: dict[str, Any]) -> AgentConfig:
        """Create AgentConfig instance from agent data"""
        # Get default template
        self.load_agent_schema()
        default_agent = self._agents_schema.get("default_agent", {})

        # Merge with agent-specific data
        merged_data = self._deep_merge(default_agent, agent_data)

        config = AgentConfig(name=agent_name)

        # Basic information
        config.description = merged_data.get("description", "")

        # AI Backend configuration
        ai_backend = merged_data.get("ai_backend", {})
        config.ai_provider = ai_backend.get("provider", config.ai_provider)
        config.ai_model = ai_backend.get("model", config.ai_model)
        config.ai_parameters = ai_backend.get("parameters", {})
        config.ai_provider_config = ai_backend.get("provider_config", {})

        # Memory configuration
        memory_config = merged_data.get("memory", {})
        config.memory_enabled = memory_config.get("enabled", config.memory_enabled)
        config.memory_database = memory_config.get("database", config.memory_database)
        config.memory_embedding_model = memory_config.get(
            "embedding_model", config.memory_embedding_model
        )
        config.memory_evolution_threshold = memory_config.get(
            "evolution_threshold", config.memory_evolution_threshold
        )

        # Personality configuration
        personality = merged_data.get("personality", {})
        config.personality_traits = personality.get("traits", [])
        config.communication_style = personality.get(
            "communication_style", config.communication_style
        )
        config.expertise_areas = personality.get("expertise_areas", [])

        # Capabilities
        capabilities = merged_data.get("capabilities", {})
        config.functions = capabilities.get("functions", [])
        config.tools = capabilities.get("tools", [])
        config.integrations = capabilities.get("integrations", [])

        # Constraints
        constraints = merged_data.get("constraints", {})
        config.max_tokens = constraints.get("max_tokens", config.max_tokens)
        config.timeout_seconds = constraints.get("timeout_seconds", config.timeout_seconds)
        config.rate_limits = constraints.get("rate_limits", {})

        return config

    def _normalize_ai_backend(self, config: AgentConfig) -> AgentConfig:
        """Normalize AI backend configuration for the provider"""
        # Map standard model name to provider-specific name
        config.ai_model = self.get_model_mapping(config.ai_model, config.ai_provider)

        # Normalize parameters for the provider
        config.ai_parameters = self.normalize_parameters(config.ai_parameters, config.ai_provider)

        # Merge with provider-specific defaults
        provider_config = self.get_provider_config(config.ai_provider)
        provider_defaults = provider_config.get("model_parameters", {})

        # Provider defaults don't override explicit parameters
        for key, value in provider_defaults.items():
            if key not in config.ai_parameters:
                config.ai_parameters[key] = value

        return config

    def _create_default_agent_config(self, agent_name: str) -> AgentConfig:
        """Create a default agent configuration"""
        return AgentConfig(
            name=agent_name,
            description=f"Default configuration for {agent_name}",
            ai_provider="ollama",
            ai_model="llama3.2:3b",
            ai_parameters={"temperature": 0.7, "max_tokens": 2048, "top_p": 0.9},
        )

    def _get_default_schema(self) -> dict[str, Any]:
        """Get default agent schema when config file is not available"""
        return {
            "default_agent": {
                "name": "default",
                "description": "Base agent configuration",
                "ai_backend": {
                    "provider": "ollama",
                    "model": "llama3.2:3b",
                    "parameters": {
                        "temperature": 0.7,
                        "max_tokens": 2048,
                        "top_p": 0.9,
                    },
                },
                "memory": {
                    "enabled": True,
                    "database": "long-term",
                    "embedding_model": "all-MiniLM-L6-v2",
                    "evolution_threshold": 5,
                },
            },
            "providers": {
                "ollama": {
                    "base_url": "localhost:11434",
                    "endpoints": {"chat": "/api/chat", "generate": "/api/generate"},
                }
            },
            "model_mappings": {"llama-3.2-3b": {"ollama": "llama3.2:3b"}},
            "parameter_mappings": {"max_tokens": {"ollama": "num_predict"}},
        }


# Global agent config loader instance
_agent_config_loader: AgentConfigLoader | None = None


def get_agent_config_loader() -> AgentConfigLoader:
    """Get the global agent configuration loader instance"""
    global _agent_config_loader
    if _agent_config_loader is None:
        _agent_config_loader = AgentConfigLoader()
    return _agent_config_loader


def load_agent_config(agent_name: str) -> AgentConfig:
    """Load configuration for a specific agent"""
    loader = get_agent_config_loader()
    return loader.load_agent_config(agent_name)


def get_provider_config(provider: str) -> dict[str, Any]:
    """Get configuration for a specific AI provider"""
    loader = get_agent_config_loader()
    return loader.get_provider_config(provider)


def build_provider_url(provider: str, endpoint: str = "") -> str:
    """Build URL for a provider endpoint"""
    loader = get_agent_config_loader()
    return loader.build_provider_url(provider, endpoint)
