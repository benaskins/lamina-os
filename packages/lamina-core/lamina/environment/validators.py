# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Environment Configuration Validators

Provides validation for environment configurations to ensure
consistency, security, and adherence to Lamina OS principles.
"""

import logging
from typing import Any

from .config import ENVIRONMENT_SIGILS, EnvironmentConfig

logger = logging.getLogger(__name__)


class EnvironmentValidationError(Exception):
    """Raised when environment configuration validation fails."""

    pass


def validate_environment_config(config: EnvironmentConfig) -> None:
    """
    Validate environment configuration comprehensively.

    Args:
        config: EnvironmentConfig to validate

    Raises:
        EnvironmentValidationError: If validation fails
    """
    errors = []

    # Basic configuration validation
    errors.extend(_validate_basic_config(config))

    # Sigil validation (Clara's breath markers)
    errors.extend(_validate_sigil_consistency(config))

    # Service configuration validation
    errors.extend(_validate_services_config(config))

    # Security configuration validation (Vesna's requirements)
    errors.extend(_validate_security_config(config))

    # Resource configuration validation
    errors.extend(_validate_resources_config(config))

    # Environment-specific validation
    errors.extend(_validate_environment_specific(config))

    if errors:
        error_msg = f"Environment '{config.name}' validation failed:\n" + "\n".join(
            f"  - {e}" for e in errors
        )
        raise EnvironmentValidationError(error_msg)

    logger.info(f"{config.sigil} Environment '{config.name}' validation passed")


def _validate_basic_config(config: EnvironmentConfig) -> list[str]:
    """Validate basic configuration fields."""
    errors = []

    if not config.name:
        errors.append("Environment name is required")

    if not config.sigil:
        errors.append("Environment sigil is required")

    if not config.type:
        errors.append("Environment type is required")

    if config.type not in ["docker-compose", "containerized", "kubernetes"]:
        errors.append(f"Invalid environment type: {config.type}")

    if not config.description:
        errors.append("Environment description is required")

    return errors


def _validate_sigil_consistency(config: EnvironmentConfig) -> list[str]:
    """Validate sigil consistency (Clara's breath markers)."""
    errors = []

    expected_sigil = ENVIRONMENT_SIGILS.get(config.name)
    if expected_sigil and config.sigil != expected_sigil:
        errors.append(
            f"Sigil mismatch: expected '{expected_sigil}' for {config.name}, got '{config.sigil}'"
        )

    # Check sigil in service environment variables
    for service_name, service_config in config.services.items():
        env_vars = service_config.get("environment", {})
        if isinstance(env_vars, dict):
            service_sigil = env_vars.get("SIGIL")
            if service_sigil and service_sigil != config.sigil:
                errors.append(
                    f"Service '{service_name}' sigil mismatch: expected '{config.sigil}', got '{service_sigil}'"
                )

    # Check sigil in logging format
    log_format = config.logging.get("format", "")
    if log_format and config.sigil not in log_format:
        errors.append(f"Logging format missing sigil '{config.sigil}'")

    return errors


def _validate_services_config(config: EnvironmentConfig) -> list[str]:
    """Validate services configuration."""
    errors = []

    if not config.services:
        errors.append("At least one service must be configured")
        return errors

    required_services = ["lamina-core"]
    for service in required_services:
        if service not in config.services:
            errors.append(f"Required service '{service}' not configured")

    # Validate individual service configurations
    for service_name, service_config in config.services.items():
        service_errors = _validate_service_config(service_name, service_config, config)
        errors.extend(service_errors)

    return errors


def _validate_service_config(
    service_name: str, service_config: dict[str, Any], env_config: EnvironmentConfig
) -> list[str]:
    """Validate individual service configuration."""
    errors = []

    if not isinstance(service_config, dict):
        errors.append(f"Service '{service_name}' configuration must be a dictionary")
        return errors

    # Environment-specific validation
    if env_config.type == "kubernetes":
        # Kubernetes-specific validation
        if "image" not in service_config:
            errors.append(f"Kubernetes service '{service_name}' missing image specification")

        if "resources" in service_config:
            resources = service_config["resources"]
            if "requests" not in resources or "limits" not in resources:
                errors.append(
                    f"Kubernetes service '{service_name}' should specify both resource requests and limits"
                )

    elif env_config.type == "docker-compose":
        # Docker Compose validation
        if "image" not in service_config and "build" not in service_config:
            errors.append(
                f"Docker Compose service '{service_name}' must specify either image or build"
            )

    # Validate environment variables
    env_vars = service_config.get("environment", {})
    if isinstance(env_vars, dict):
        if "ENV" not in env_vars:
            errors.append(f"Service '{service_name}' missing ENV environment variable")
        elif env_vars["ENV"] != env_config.name:
            errors.append(
                f"Service '{service_name}' ENV mismatch: expected '{env_config.name}', got '{env_vars['ENV']}'"
            )

    return errors


def _validate_security_config(config: EnvironmentConfig) -> list[str]:
    """Validate security configuration (Vesna's requirements)."""
    errors = []

    if not config.security:
        errors.append("Security configuration is required")
        return errors

    # Production security requirements
    if config.is_production():
        required_security = ["mtls", "rbac", "network_policies", "secrets_encryption"]
        for req in required_security:
            if not config.security.get(req, False):
                errors.append(f"Production environment requires {req} to be enabled")

    # Development security warnings (not errors)
    if config.is_development():
        if config.security.get("mtls", False):
            logger.warning(f"{config.sigil} mTLS enabled in development may slow iteration")

    # Test environment security requirements
    if config.is_test():
        if config.security.get("network_policies", False):
            # Network policies should allow test isolation
            pass

    return errors


def _validate_resources_config(config: EnvironmentConfig) -> list[str]:
    """Validate resource configuration."""
    errors = []

    if not config.resources:
        return errors  # Resources are optional for some environments

    # Validate resource format
    for resource_type in ["total_memory", "total_cpu"]:
        if resource_type in config.resources:
            resource_value = config.resources[resource_type]
            if not isinstance(resource_value, str | int | float):
                errors.append(f"Resource '{resource_type}' must be string, int, or float")

    # Environment-specific resource validation
    if config.is_production():
        required_resources = ["total_memory", "total_cpu"]
        for req in required_resources:
            if req not in config.resources:
                errors.append(f"Production environment should specify {req}")

    return errors


def _validate_environment_specific(config: EnvironmentConfig) -> list[str]:
    """Validate environment-specific configurations."""
    errors = []

    if config.is_development():
        errors.extend(_validate_development_config(config))
    elif config.is_test():
        errors.extend(_validate_test_config(config))
    elif config.is_production():
        errors.extend(_validate_production_config(config))

    return errors


def _validate_development_config(config: EnvironmentConfig) -> list[str]:
    """Validate development-specific configuration."""
    errors = []

    # Development should support debugging
    if not config.supports_feature("debug_ports"):
        logger.warning(
            f"{config.sigil} Development environment should enable debug_ports for better DX"
        )

    # Hot reload recommended for development
    if not config.supports_feature("hot_reload"):
        logger.warning(f"{config.sigil} Development environment should enable hot_reload")

    return errors


def _validate_test_config(config: EnvironmentConfig) -> list[str]:
    """Validate test-specific configuration."""
    errors = []

    # Test environment should be ephemeral
    if not config.supports_feature("ephemeral"):
        errors.append("Test environment should be ephemeral")

    # Test environment should support isolation
    if not config.supports_feature("isolation"):
        errors.append("Test environment should support strict isolation")

    # Test configuration section validation
    if config.testing:
        if "timeout_per_test" in config.testing:
            timeout = config.testing["timeout_per_test"]
            if not isinstance(timeout, str) or not timeout.endswith("s"):
                errors.append("Test timeout should be string with 's' suffix")

    return errors


def _validate_production_config(config: EnvironmentConfig) -> list[str]:
    """Validate production-specific configuration."""
    errors = []

    # Production should have monitoring
    if not config.supports_feature("comprehensive_monitoring"):
        errors.append("Production environment requires comprehensive monitoring")

    # Production should have auto-scaling
    if not config.supports_feature("auto_scaling"):
        logger.warning(f"{config.sigil} Production environment should enable auto_scaling")

    # Validate autoscaling configuration
    if config.autoscaling:
        for service_name, scaling_config in config.autoscaling.items():
            if not isinstance(scaling_config, dict):
                errors.append(f"Autoscaling config for '{service_name}' must be dict")
                continue

            required_scaling = ["min_replicas", "max_replicas"]
            for req in required_scaling:
                if req not in scaling_config:
                    errors.append(f"Autoscaling for '{service_name}' missing {req}")

    # Validate monitoring configuration
    if config.monitoring:
        if "prometheus" in config.monitoring and not config.monitoring["prometheus"].get(
            "enabled", False
        ):
            errors.append("Production monitoring should enable Prometheus")

    return errors


def validate_environment_transition(from_env: str, to_env: str) -> list[str]:
    """
    Validate environment transition rules.

    Args:
        from_env: Source environment name
        to_env: Target environment name

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    valid_transitions = {
        "development": ["test", "production"],
        "test": ["production"],
        "production": [],  # No transitions from production
    }

    if from_env not in valid_transitions:
        errors.append(f"Unknown source environment: {from_env}")
        return errors

    if to_env not in valid_transitions[from_env]:
        allowed = ", ".join(valid_transitions[from_env]) or "none"
        errors.append(f"Invalid transition from {from_env} to {to_env}. Allowed: {allowed}")

    # Production transition requires extra validation
    if to_env == "production":
        if from_env != "test":
            errors.append("Production deployment should come from test environment")

    return errors
