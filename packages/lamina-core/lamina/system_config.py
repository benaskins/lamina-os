# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
System Configuration Loader for Lamina OS

This module provides centralized configuration management for system-wide settings,
agent orchestration, and runtime behavior. It supports environment-specific overrides
and provides a unified interface for accessing configuration values.
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


@dataclass
class SystemConfig:
    """System configuration data class"""

    version: str = "1.0.0"
    sanctuary_path: str = "sanctuary"
    default_agent: str = "example"

    # Agent management
    agent_discovery_enabled: bool = True
    agent_scan_interval: int = 60
    agent_defaults: dict[str, Any] = field(default_factory=dict)
    agent_registry: dict[str, dict[str, Any]] = field(default_factory=dict)

    # API configuration
    api_host: str = "localhost"
    api_port: int = 8001
    api_ssl_enabled: bool = True
    api_max_sessions: int = 100
    api_request_timeout: int = 30

    # Memory system
    memory_embedding_model: str = "all-MiniLM-L6-v2"
    memory_evolution_threshold: int = 5
    memory_max_per_agent: int = 10000
    memory_retention_days: int = 365

    # AI defaults
    ai_default_provider: str = "ollama"
    ai_fallback_providers: list = field(default_factory=lambda: ["huggingface"])
    ai_generation_defaults: dict[str, Any] = field(default_factory=dict)

    # Observability
    log_level: str = "INFO"
    metrics_enabled: bool = True
    trace_conversations: bool = True
    performance_monitoring: bool = True

    # Security
    ssl_verify_client: bool = True
    session_encryption: bool = True
    memory_encryption: bool = False


class SystemConfigLoader:
    """Loads and manages system configuration with environment overrides"""

    def __init__(self, config_dir: str | None = None, sanctuary_path: str | None = None):
        self.config_dir = Path(config_dir or "config")
        self.sanctuary_path = Path(sanctuary_path or "sanctuary")
        self.system_config_path = self.config_dir / "system.yaml"
        self.sanctuary_config_path = self.sanctuary_path / "system" / "local.yaml"
        self.environment = os.getenv("LAMINA_ENV", "development")
        self._config: SystemConfig | None = None
        self._raw_config: dict[str, Any] | None = None

    def load(self) -> SystemConfig:
        """Load system configuration with environment overrides"""
        if self._config is not None:
            return self._config

        try:
            # Load base configuration
            if not self.system_config_path.exists():
                logger.warning(
                    f"System config not found at {self.system_config_path}, using defaults"
                )
                self._raw_config = {}
            else:
                with open(self.system_config_path) as f:
                    self._raw_config = yaml.safe_load(f) or {}

            # Load sanctuary-specific overrides
            self._load_sanctuary_overrides()

            # Apply environment variable substitution
            self._raw_config = self._substitute_env_vars(self._raw_config)

            # Apply environment-specific overrides
            self._apply_environment_overrides()

            # Create SystemConfig instance
            self._config = self._create_system_config()

            logger.info(f"Loaded system configuration for environment: {self.environment}")
            return self._config

        except Exception as e:
            logger.error(f"Failed to load system configuration: {e}")
            # Return default configuration on error
            self._config = SystemConfig()
            return self._config

    def reload(self) -> SystemConfig:
        """Reload configuration from disk"""
        self._config = None
        self._raw_config = None
        return self.load()

    def get_agent_config(self, agent_name: str) -> dict[str, Any]:
        """Get configuration for a specific agent"""
        config = self.load()
        agent_config = config.agent_registry.get(agent_name, {})

        # Merge with defaults
        merged_config = {**config.agent_defaults, **agent_config}
        merged_config["name"] = agent_name

        return merged_config

    def get_api_config(self) -> dict[str, Any]:
        """Get API server configuration"""
        config = self.load()
        return {
            "host": config.api_host,
            "port": config.api_port,
            "ssl_enabled": config.api_ssl_enabled,
            "max_sessions": config.api_max_sessions,
            "request_timeout": config.api_request_timeout,
        }

    def get_memory_config(self) -> dict[str, Any]:
        """Get memory system configuration"""
        config = self.load()
        return {
            "embedding_model": config.memory_embedding_model,
            "evolution_threshold": config.memory_evolution_threshold,
            "max_memories_per_agent": config.memory_max_per_agent,
            "retention_days": config.memory_retention_days,
        }

    def get_ai_config(self) -> dict[str, Any]:
        """Get AI system configuration"""
        config = self.load()
        return {
            "default_provider": config.ai_default_provider,
            "fallback_providers": config.ai_fallback_providers,
            "generation_defaults": config.ai_generation_defaults,
        }

    def get_observability_config(self) -> dict[str, Any]:
        """Get observability configuration"""
        config = self.load()
        return {
            "log_level": config.log_level,
            "metrics_enabled": config.metrics_enabled,
            "trace_conversations": config.trace_conversations,
            "performance_monitoring": config.performance_monitoring,
        }

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

    def _load_sanctuary_overrides(self):
        """Load sanctuary-specific configuration overrides"""
        if self.sanctuary_config_path.exists():
            try:
                with open(self.sanctuary_config_path) as f:
                    sanctuary_config = yaml.safe_load(f) or {}

                logger.info(f"Loading sanctuary overrides from {self.sanctuary_config_path}")
                self._raw_config = self._deep_merge(self._raw_config, sanctuary_config)
            except Exception as e:
                logger.warning(f"Failed to load sanctuary config: {e}")
        else:
            logger.debug(f"No sanctuary config found at {self.sanctuary_config_path}")

    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides"""
        environments = self._raw_config.get("environments", {})
        env_overrides = environments.get(self.environment, {})

        if env_overrides:
            logger.info(f"Applying {self.environment} environment overrides")
            self._raw_config = self._deep_merge(self._raw_config, env_overrides)

    def _deep_merge(self, base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        """Deep merge two dictionaries"""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _create_system_config(self) -> SystemConfig:
        """Create SystemConfig instance from raw configuration"""
        config = SystemConfig()

        # Lamina settings
        lamina_config = self._raw_config.get("lamina", {})
        config.version = lamina_config.get("version", config.version)
        config.sanctuary_path = lamina_config.get("sanctuary_path", config.sanctuary_path)
        config.default_agent = lamina_config.get("default_agent", config.default_agent)

        # Agent settings
        agents_config = self._raw_config.get("agents", {})
        discovery_config = agents_config.get("discovery", {})
        config.agent_discovery_enabled = discovery_config.get(
            "auto_load", config.agent_discovery_enabled
        )
        config.agent_scan_interval = discovery_config.get(
            "scan_interval_seconds", config.agent_scan_interval
        )
        config.agent_defaults = agents_config.get("defaults", {})
        config.agent_registry = agents_config.get("registry", {})

        # API settings
        api_config = self._raw_config.get("api", {})
        config.api_host = api_config.get("default_host", config.api_host)
        config.api_port = api_config.get("default_port", config.api_port)
        config.api_ssl_enabled = api_config.get("ssl_enabled", config.api_ssl_enabled)
        config.api_max_sessions = api_config.get("max_sessions", config.api_max_sessions)
        config.api_request_timeout = api_config.get(
            "request_timeout_seconds", config.api_request_timeout
        )

        # Memory settings
        memory_config = self._raw_config.get("memory", {})
        config.memory_embedding_model = memory_config.get(
            "default_embedding_model", config.memory_embedding_model
        )
        config.memory_evolution_threshold = memory_config.get(
            "evolution_threshold", config.memory_evolution_threshold
        )
        config.memory_max_per_agent = memory_config.get(
            "max_memories_per_agent", config.memory_max_per_agent
        )
        config.memory_retention_days = memory_config.get(
            "retention_days", config.memory_retention_days
        )

        # AI settings
        ai_config = self._raw_config.get("ai", {})
        config.ai_default_provider = ai_config.get("default_provider", config.ai_default_provider)
        config.ai_fallback_providers = ai_config.get(
            "fallback_providers", config.ai_fallback_providers
        )
        config.ai_generation_defaults = ai_config.get("generation_defaults", {})

        # Observability settings
        obs_config = self._raw_config.get("observability", {})
        config.log_level = obs_config.get("default_log_level", config.log_level)
        config.metrics_enabled = obs_config.get("metrics_enabled", config.metrics_enabled)
        config.trace_conversations = obs_config.get(
            "trace_conversations", config.trace_conversations
        )
        config.performance_monitoring = obs_config.get(
            "performance_monitoring", config.performance_monitoring
        )

        # Security settings
        security_config = self._raw_config.get("security", {})
        config.ssl_verify_client = security_config.get(
            "ssl_verify_client", config.ssl_verify_client
        )
        config.session_encryption = security_config.get(
            "session_encryption", config.session_encryption
        )
        config.memory_encryption = security_config.get(
            "memory_encryption", config.memory_encryption
        )

        return config


# Global system config loader instance
_system_config_loader: SystemConfigLoader | None = None


def get_system_config() -> SystemConfig:
    """Get the global system configuration instance"""
    global _system_config_loader
    if _system_config_loader is None:
        _system_config_loader = SystemConfigLoader()
    return _system_config_loader.load()


def reload_system_config() -> SystemConfig:
    """Reload the global system configuration from disk"""
    global _system_config_loader
    if _system_config_loader is None:
        _system_config_loader = SystemConfigLoader()
    return _system_config_loader.reload()


def get_agent_config(agent_name: str) -> dict[str, Any]:
    """Get configuration for a specific agent"""
    global _system_config_loader
    if _system_config_loader is None:
        _system_config_loader = SystemConfigLoader()
    return _system_config_loader.get_agent_config(agent_name)


def get_api_config() -> dict[str, Any]:
    """Get API server configuration"""
    global _system_config_loader
    if _system_config_loader is None:
        _system_config_loader = SystemConfigLoader()
    return _system_config_loader.get_api_config()


def get_memory_config() -> dict[str, Any]:
    """Get memory system configuration"""
    global _system_config_loader
    if _system_config_loader is None:
        _system_config_loader = SystemConfigLoader()
    return _system_config_loader.get_memory_config()


def get_ai_config() -> dict[str, Any]:
    """Get AI system configuration"""
    global _system_config_loader
    if _system_config_loader is None:
        _system_config_loader = SystemConfigLoader()
    return _system_config_loader.get_ai_config()


def get_observability_config() -> dict[str, Any]:
    """Get observability configuration"""
    global _system_config_loader
    if _system_config_loader is None:
        _system_config_loader = SystemConfigLoader()
    return _system_config_loader.get_observability_config()
