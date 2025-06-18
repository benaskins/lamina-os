#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

"""
Configuration management for Lamina Dashboard
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class DashboardConfig:
    """Configuration manager for Lamina Dashboard."""

    def __init__(self, environment: Optional[str] = None):
        self.environment = environment or os.getenv("LAMINA_ENV", "production")
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment-specific files."""

        # Default configuration
        defaults = {
            "server": {
                "host": "0.0.0.0",
                "port": 5001,
                "autoreload": False,
                "debug": False,
                "workers": 1,
                "worker_class": "eventlet",
                "timeout": 30,
                "keepalive": 2,
            },
            "monitoring": {
                "update_interval": 5,
                "prometheus_timeout": 10,
                "kubernetes_timeout": 30,
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            },
        }

        # Look for config files in order of precedence
        config_paths = [
            f"/etc/lamina/dashboard/{self.environment}.yaml",  # System config
            f"~/.lamina/dashboard/{self.environment}.yaml",  # User config
            f"./config/{self.environment}.yaml",  # Local config
            "./config/dashboard.yaml",  # Fallback
        ]

        config = defaults.copy()

        for path_str in config_paths:
            path = Path(path_str).expanduser()
            if path.exists():
                try:
                    with open(path, "r") as f:
                        env_config = yaml.safe_load(f)
                        if env_config:
                            config = self._deep_merge(config, env_config)
                            print(f"📄 Loaded config from: {path}")
                            break
                except Exception as e:
                    print(f"⚠️ Failed to load config from {path}: {e}")

        # Override with environment variables
        self._apply_env_overrides(config)

        return config

    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def _apply_env_overrides(self, config: Dict[str, Any]) -> None:
        """Apply environment variable overrides."""

        # Server overrides
        if os.getenv("DASHBOARD_HOST"):
            config["server"]["host"] = os.getenv("DASHBOARD_HOST")
        if os.getenv("DASHBOARD_PORT"):
            config["server"]["port"] = int(os.getenv("DASHBOARD_PORT"))
        if os.getenv("DASHBOARD_DEBUG"):
            config["server"]["debug"] = os.getenv("DASHBOARD_DEBUG").lower() == "true"
        if os.getenv("DASHBOARD_AUTORELOAD"):
            config["server"]["autoreload"] = os.getenv("DASHBOARD_AUTORELOAD").lower() == "true"

        # Monitoring overrides
        if os.getenv("MONITORING_INTERVAL"):
            config["monitoring"]["update_interval"] = int(os.getenv("MONITORING_INTERVAL"))

        # Logging overrides
        if os.getenv("LOG_LEVEL"):
            config["logging"]["level"] = os.getenv("LOG_LEVEL").upper()

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'server.port')."""
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration section."""
        return self.config.get("server", {})

    def get_monitoring_config(self) -> Dict[str, Any]:
        """Get monitoring configuration section."""
        return self.config.get("monitoring", {})

    def should_use_gunicorn(self) -> bool:
        """Determine if we should use Gunicorn based on configuration."""
        # Use Gunicorn unless explicitly in development mode with autoreload
        return not (self.environment == "development" and self.get("server.autoreload", False))

    def __str__(self) -> str:
        """String representation for debugging."""
        return f"DashboardConfig(env={self.environment}, config={self.config})"
