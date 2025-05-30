# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Environment Configuration Management

Handles loading, validation, and management of environment-specific
configurations with breath-aware markers and ritual integration.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# Breath markers for environment context
ENVIRONMENT_SIGILS = {"development": "🜂", "test": "🜁", "production": "🜄"}


@dataclass
class EnvironmentConfig:
    """
    Environment configuration with breath-aware markers.

    Represents a complete environment configuration including
    services, resources, security, and ritual aspects.
    """

    name: str
    sigil: str
    type: str
    description: str
    features: dict[str, Any] = field(default_factory=dict)
    services: dict[str, Any] = field(default_factory=dict)
    volumes: dict[str, Any] = field(default_factory=dict)
    networks: dict[str, Any] = field(default_factory=dict)
    breath: dict[str, Any] = field(default_factory=dict)
    security: dict[str, Any] = field(default_factory=dict)
    logging: dict[str, Any] = field(default_factory=dict)
    resources: dict[str, Any] = field(default_factory=dict)

    # Environment-specific sections
    development: dict[str, Any] | None = None
    testing: dict[str, Any] | None = None
    autoscaling: dict[str, Any] | None = None
    monitoring: dict[str, Any] | None = None
    backup: dict[str, Any] | None = None
    deployment: dict[str, Any] | None = None

    def __post_init__(self):
        """Validate and set defaults after initialization."""
        if self.sigil not in ENVIRONMENT_SIGILS.values():
            expected_sigil = ENVIRONMENT_SIGILS.get(self.name, "❓")
            logger.warning(
                f"Environment {self.name} sigil mismatch. Expected: {expected_sigil}, Got: {self.sigil}"
            )

        # Set default logging format with sigil
        if "format" not in self.logging:
            self.logging["format"] = (
                f"{self.sigil} [%(asctime)s] %(name)s - %(levelname)s - %(message)s"
            )

        # Ensure sigil is set in environment variables for all services
        for _service_name, service_config in self.services.items():
            if "environment" in service_config:
                service_config["environment"]["SIGIL"] = self.sigil

    def get_sigil_prefix(self) -> str:
        """Get the sigil prefix for CLI output."""
        return f"{self.sigil} "

    def get_log_format(self) -> str:
        """Get the logging format with sigil integration."""
        return self.logging.get(
            "format", f"{self.sigil} [%(asctime)s] %(name)s - %(levelname)s - %(message)s"
        )

    def is_production(self) -> bool:
        """Check if this is a production environment."""
        return self.name == "production"

    def is_development(self) -> bool:
        """Check if this is a development environment."""
        return self.name == "development"

    def is_test(self) -> bool:
        """Check if this is a test environment."""
        return self.name == "test"

    def supports_feature(self, feature: str) -> bool:
        """Check if environment supports a specific feature."""
        return self.features.get(feature, False)

    def get_service_config(self, service_name: str) -> dict[str, Any] | None:
        """Get configuration for a specific service."""
        return self.services.get(service_name)

    def get_resource_limits(self) -> dict[str, Any]:
        """Get resource limits for the environment."""
        return self.resources.copy()

    def get_security_config(self) -> dict[str, Any]:
        """Get security configuration."""
        return self.security.copy()

    def get_breath_config(self) -> dict[str, Any]:
        """Get breath-aware configuration."""
        return self.breath.copy()


def load_environment_config(
    environment_name: str, config_path: Path | None = None
) -> EnvironmentConfig:
    """
    Load environment configuration from YAML file.

    Args:
        environment_name: Name of environment (development, test, production)
        config_path: Optional path to config file. If None, uses default location.

    Returns:
        EnvironmentConfig instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    if config_path is None:
        # Default to environments/{name}/config.yaml relative to project root
        project_root = Path(__file__).parent.parent.parent.parent.parent
        config_path = project_root / "environments" / environment_name / "config.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Environment config not found: {config_path}")

    logger.info(f"Loading environment config: {config_path}")

    try:
        with open(config_path) as f:
            config_data = yaml.safe_load(f)

        # Extract environment section
        env_data = config_data.get("environment", {})

        # Create EnvironmentConfig with all sections
        config = EnvironmentConfig(
            name=env_data.get("name", environment_name),
            sigil=env_data.get("sigil", ENVIRONMENT_SIGILS.get(environment_name, "❓")),
            type=env_data.get("type", "unknown"),
            description=env_data.get("description", f"{environment_name} environment"),
            features=config_data.get("features", {}),
            services=config_data.get("services", {}),
            volumes=config_data.get("volumes", {}),
            networks=config_data.get("networks", {}),
            breath=config_data.get("breath", {}),
            security=config_data.get("security", {}),
            logging=config_data.get("logging", {}),
            resources=config_data.get("resources", {}),
            development=config_data.get("development"),
            testing=config_data.get("testing"),
            autoscaling=config_data.get("autoscaling"),
            monitoring=config_data.get("monitoring"),
            backup=config_data.get("backup"),
            deployment=config_data.get("deployment"),
        )

        logger.info(f"{config.sigil} Loaded environment config for {config.name}")
        return config

    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in config file {config_path}: {e}")
    except Exception as e:
        raise ValueError(f"Error loading config from {config_path}: {e}")


def get_available_environments(environments_root: Path | None = None) -> list[str]:
    """
    Get list of available environment names.

    Args:
        environments_root: Root directory containing environment configs

    Returns:
        List of environment names
    """
    if environments_root is None:
        project_root = Path(__file__).parent.parent.parent.parent.parent
        environments_root = project_root / "environments"

    if not environments_root.exists():
        return []

    environments = []
    for env_dir in environments_root.iterdir():
        if env_dir.is_dir() and (env_dir / "config.yaml").exists():
            environments.append(env_dir.name)

    return sorted(environments)


def validate_environment_name(environment_name: str) -> bool:
    """
    Validate that environment name is supported.

    Args:
        environment_name: Name to validate

    Returns:
        True if valid, False otherwise
    """
    return environment_name in ["development", "test", "production"]


def get_environment_sigil(environment_name: str) -> str:
    """
    Get the breath marker sigil for an environment.

    Args:
        environment_name: Environment name

    Returns:
        Sigil character for the environment
    """
    return ENVIRONMENT_SIGILS.get(environment_name, "❓")
