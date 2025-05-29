# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

import os
import re
from pathlib import Path
from typing import Any

import yaml


class InfrastructureConfig:
    """
    Enhanced configuration loader for infrastructure settings.

    Handles environment-specific overrides, URL building, and environment variable substitution.
    """

    def __init__(
        self,
        config_file: str = "config/infrastructure.yaml",
        environment: str | None = None,
    ):
        """
        Initialize the infrastructure configuration.

        Args:
            config_file: Path to the infrastructure configuration file
            environment: Environment name (development, test, production).
                        If None, uses LAMINA_ENV or default_environment from config
        """
        self.config_file = config_file
        self.environment = environment or os.getenv("LAMINA_ENV")
        self._config = None
        self._load_config()

    def _load_config(self):
        """Load and process the configuration file."""
        config_path = Path(self.config_file)

        if not config_path.exists():
            raise FileNotFoundError(f"Infrastructure configuration file not found: {config_path}")

        with open(config_path) as file:
            self._config = yaml.safe_load(file)

        # Set environment if not specified
        if not self.environment:
            self.environment = self._config.get("default_environment", "development")

        # Apply environment-specific overrides
        self._apply_environment_overrides()

        # Substitute environment variables
        self._substitute_environment_variables()

    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides."""
        if "environments" not in self._config:
            return

        env_config = self._config["environments"].get(self.environment, {})
        if not env_config:
            return

        # Check if we're running inside a container
        # If so, skip environment overrides for service connections to use internal networking
        if self._is_running_in_container():
            # Only apply non-service overrides (like SSL settings)
            filtered_env_config = {}
            for key, value in env_config.items():
                if key != "services":  # Skip service overrides
                    filtered_env_config[key] = value
            env_config = filtered_env_config

        # Deep merge environment config into base config
        self._deep_merge(self._config, env_config)

    def _is_running_in_container(self) -> bool:
        """Check if we're running inside a Docker container."""
        # Check for Docker-specific files/environment
        return (
            os.path.exists("/.dockerenv")
            or os.path.exists("/proc/1/cgroup")
            and any("docker" in line for line in open("/proc/1/cgroup").readlines())
        )

    def _deep_merge(self, base: dict, override: dict):
        """Deep merge override dictionary into base dictionary."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _substitute_environment_variables(self):
        """Substitute environment variables in configuration values."""
        self._config = self._substitute_vars_recursive(self._config)

    def _substitute_vars_recursive(self, obj):
        """Recursively substitute environment variables in configuration."""
        if isinstance(obj, dict):
            return {key: self._substitute_vars_recursive(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._substitute_vars_recursive(item) for item in obj]
        elif isinstance(obj, str):
            return self._substitute_env_vars(obj)
        else:
            return obj

    def _substitute_env_vars(self, value: str) -> str:
        """Substitute environment variables in a string value."""
        # Pattern: ${VAR_NAME} or ${VAR_NAME:-default_value}
        pattern = r"\$\{([^}]+)\}"

        def replace_var(match):
            var_expr = match.group(1)
            if ":-" in var_expr:
                var_name, default_value = var_expr.split(":-", 1)
                return os.getenv(var_name, default_value)
            else:
                return os.getenv(var_expr, match.group(0))  # Return original if not found

        return re.sub(pattern, replace_var, value)

    def get_service_config(self, service_name: str) -> dict[str, Any]:
        """Get configuration for a specific service."""
        services = self._config.get("services", {})
        if service_name not in services:
            raise ValueError(f"Service '{service_name}' not found in configuration")

        return services[service_name].copy()

    def get_service_url(self, service_name: str, endpoint: str = None) -> str:
        """
        Build a complete URL for a service endpoint.

        Args:
            service_name: Name of the service (e.g., 'ollama', 'loki')
            endpoint: Optional endpoint path (e.g., '/api/chat')

        Returns:
            Complete URL string
        """
        service_config = self.get_service_config(service_name)

        protocol = service_config.get("protocol", "http")
        host = service_config.get("host", "localhost")
        port = service_config.get("port", 80)

        base_url = f"{protocol}://{host}:{port}"

        if endpoint:
            # Remove leading slash if present to avoid double slashes
            endpoint = endpoint.lstrip("/")
            return f"{base_url}/{endpoint}"

        return base_url

    def get_service_endpoint_url(self, service_name: str, endpoint_name: str) -> str:
        """
        Get a predefined endpoint URL for a service.

        Args:
            service_name: Name of the service
            endpoint_name: Name of the endpoint (as defined in config)

        Returns:
            Complete URL string
        """
        service_config = self.get_service_config(service_name)
        endpoints = service_config.get("endpoints", {})

        if endpoint_name not in endpoints:
            raise ValueError(f"Endpoint '{endpoint_name}' not found for service '{service_name}'")

        endpoint_path = endpoints[endpoint_name]
        return self.get_service_url(service_name, endpoint_path)

    def get_ssl_config(self) -> dict[str, Any]:
        """Get SSL/TLS configuration."""
        return self._config.get("ssl", {}).copy()

    def get_cert_path(self, cert_type: str, file_type: str) -> str:
        """
        Get the full path to a certificate file.

        Args:
            cert_type: Type of certificate ('ca', service name like 'agent', 'ollama', etc.)
            file_type: Type of file ('cert_file', 'key_file')

        Returns:
            Full path to the certificate file
        """
        ssl_config = self.get_ssl_config()
        cert_dir = ssl_config.get("cert_dir", "lamina/api/certs")

        # Handle CA certificates
        if cert_type == "ca":
            if cert_type not in ssl_config:
                raise ValueError(f"Certificate type '{cert_type}' not found in SSL configuration")
            cert_config = ssl_config[cert_type]
        else:
            # Handle service certificates
            services = ssl_config.get("services", {})
            if cert_type not in services:
                raise ValueError(
                    f"Service certificate '{cert_type}' not found in SSL configuration"
                )
            cert_config = services[cert_type]

        if file_type not in cert_config:
            raise ValueError(
                f"File type '{file_type}' not found for certificate type '{cert_type}'"
            )

        cert_file = cert_config[file_type]
        return str(Path(cert_dir) / cert_file)

    def get_environment(self) -> str:
        """Get the current environment name."""
        return self.environment

    def get_raw_config(self) -> dict[str, Any]:
        """Get the raw configuration dictionary (for debugging)."""
        return self._config.copy()


# Global instance for easy access
_infrastructure_config = None


def get_infrastructure_config(
    config_file: str = "config/infrastructure.yaml", environment: str | None = None
) -> InfrastructureConfig:
    """
    Get the global infrastructure configuration instance.

    Args:
        config_file: Path to the infrastructure configuration file
        environment: Environment name (only used on first call)

    Returns:
        InfrastructureConfig instance
    """
    global _infrastructure_config

    if _infrastructure_config is None:
        _infrastructure_config = InfrastructureConfig(config_file, environment)

    return _infrastructure_config


def reset_infrastructure_config():
    """Reset the global configuration instance (useful for testing)."""
    global _infrastructure_config
    _infrastructure_config = None
