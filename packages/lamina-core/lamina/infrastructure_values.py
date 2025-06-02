# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Infrastructure Values Loader for Lamina

This module loads agent-specific infrastructure values from sanctuary configurations
and provides them for templating infrastructure components.
"""

import logging
import os
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class InfrastructureValues:
    """Container for infrastructure values"""

    def __init__(self, values: dict[str, Any]):
        self._values = values

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value using dot notation (e.g., 'agent.name')"""
        keys = key.split(".")
        value = self._values

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_agent_name(self) -> str:
        """Get the agent name"""
        return self.get("agent.name", "example")

    def get_container_config(self) -> dict[str, Any]:
        """Get container configuration"""
        return self.get("container", {})

    def get_nginx_config(self) -> dict[str, Any]:
        """Get nginx configuration"""
        return self.get("nginx", {})

    def get_ollama_config(self) -> dict[str, Any]:
        """Get ollama configuration"""
        return self.get("ollama", {})

    def get_grafana_config(self) -> dict[str, Any]:
        """Get grafana configuration"""
        return self.get("grafana", {})

    def get_vector_config(self) -> dict[str, Any]:
        """Get vector configuration"""
        return self.get("vector", {})

    def get_volumes_config(self) -> dict[str, Any]:
        """Get volumes configuration"""
        return self.get("volumes", {})

    def to_dict(self) -> dict[str, Any]:
        """Get all values as dictionary"""
        return self._values.copy()


class InfrastructureValuesLoader:
    """Loads infrastructure values from sanctuary agent configurations"""

    def __init__(self, sanctuary_path: str | None = None):
        self.sanctuary_path = Path(sanctuary_path or "sanctuary")

    def load_agent_values(self, agent_name: str) -> InfrastructureValues:
        """Load infrastructure values for a specific agent"""
        agent_dir = self.sanctuary_path / "agents" / agent_name
        values_file = agent_dir / "infrastructure.yaml"

        if not values_file.exists():
            logger.warning(
                f"No infrastructure values found for agent '{agent_name}' at {values_file}, using defaults"
            )
            return self._get_default_values(agent_name)

        try:
            with open(values_file) as f:
                values = yaml.safe_load(f) or {}

            logger.info(f"Loaded infrastructure values for agent: {agent_name}")
            return InfrastructureValues(values)

        except Exception as e:
            logger.error(f"Failed to load infrastructure values for {agent_name}: {e}")
            return self._get_default_values(agent_name)

    def _get_default_values(self, agent_name: str) -> InfrastructureValues:
        """Get default infrastructure values for an agent"""
        return InfrastructureValues(
            {
                "agent": {
                    "name": agent_name,
                    "display_name": agent_name.title(),
                    "description": f"{agent_name.title()} conversational agent",
                },
                "container": {
                    "image_tag": agent_name,
                    "environment": {
                        "AGENT_NAME": agent_name,
                        "LOG_LEVEL": "INFO",
                        "LAMINA_ENV": "production",
                    },
                },
                "nginx": {
                    "upstream_name": f"{agent_name}_backend",
                    "server_name": f"{agent_name}:8001",
                    "ssl_client_cn": agent_name,
                },
                "ollama": {
                    "model_name": agent_name,
                    "modelfile_path": f"sanctuary/agents/{agent_name}/ollama/Modelfile",
                    "preload_enabled": True,
                },
                "grafana": {
                    "dashboard_title": f"{agent_name.title()} - Agent Insights & Conversations",
                    "dashboard_tags": [agent_name, "agent", "conversations"],
                    "mindfulness_title": f"🤖 {agent_name.title()}'s Mindfulness State",
                    "mood_title": f"📊 {agent_name.title()}'s Mood (Error Rate)",
                    "activity_title": f"📈 {agent_name.title()} Activity Pattern",
                    "health_title": f"⚠️ {agent_name.title()}'s Health Alerts",
                    "voice_title": f"💬 {agent_name.title()}'s Voice - Recent Conversations",
                },
                "vector": {
                    "container_name": f"infrastructure-{agent_name}-1",
                    "log_filters": {"agent": agent_name},
                },
                "volumes": {"prefix": "lamina", "agent_specific": True},
            }
        )


# Global instance for easy access
_infrastructure_values_loader: InfrastructureValuesLoader | None = None


def get_infrastructure_values(agent_name: str) -> InfrastructureValues:
    """Get infrastructure values for a specific agent"""
    global _infrastructure_values_loader

    if _infrastructure_values_loader is None:
        _infrastructure_values_loader = InfrastructureValuesLoader()

    return _infrastructure_values_loader.load_agent_values(agent_name)


def get_current_agent_values() -> InfrastructureValues:
    """Get infrastructure values for the current agent (from AGENT_NAME env var)"""
    agent_name = os.getenv("AGENT_NAME", "example")
    return get_infrastructure_values(agent_name)
