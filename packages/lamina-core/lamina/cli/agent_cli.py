# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Agent CLI - Agent Creation and Management

Command-line interface for creating, configuring, and managing
individual agents within a sanctuary.
"""

import logging
from pathlib import Path
from typing import Any

import yaml

from lamina.cli.templates import get_agent_template

logger = logging.getLogger(__name__)


class AgentCLI:
    """Command-line interface for agent management"""

    def __init__(self):
        self.current_dir = Path.cwd()
        self._validate_sanctuary()

    def _validate_sanctuary(self):
        """Validate that we're in a sanctuary directory"""
        if not (self.current_dir / "lamina.yaml").exists():
            # Look for sanctuary in parent directories
            for parent in self.current_dir.parents:
                if (parent / "lamina.yaml").exists():
                    self.current_dir = parent
                    return

            raise RuntimeError(
                "Not in a lamina sanctuary. " "Run 'lamina sanctuary init <name>' to create one."
            )

    def create_agent(
        self,
        name: str,
        template: str = "conversational",
        provider: str | None = None,
        model: str | None = None,
    ) -> bool:
        """
        Create a new agent in the current sanctuary.

        Args:
            name: Agent name
            template: Agent template type
            provider: AI provider override
            model: AI model override

        Returns:
            True if successful, False otherwise
        """
        try:
            agents_dir = self.current_dir / "sanctuary" / "agents"
            agent_path = agents_dir / name

            if agent_path.exists():
                print(f"❌ Agent '{name}' already exists")
                return False

            print(f"🤖 Creating agent: {name}")

            # Create agent directory
            agent_path.mkdir(parents=True, exist_ok=True)

            # Get template configuration
            agent_config = get_agent_template(template).copy()
            agent_config["name"] = name

            # Apply overrides
            if provider:
                agent_config["ai_provider"] = provider
            if model:
                agent_config["ai_model"] = model

            # Generate agent.yaml
            self._generate_agent_config(agent_path, agent_config)

            # Generate infrastructure.yaml
            self._generate_infrastructure_config(agent_path, name, agent_config)

            # Generate known_entities.yaml
            self._generate_entities_config(agent_path, name)

            # Generate provider-specific files
            if agent_config["ai_provider"] == "ollama":
                self._generate_ollama_modelfile(agent_path, name, agent_config)

            # Update sanctuary configuration
            self._update_sanctuary_config(name, agent_config)

            print(f"✅ Agent '{name}' created successfully!")
            print(f"📁 Location: {agent_path}")
            print("\n📋 Next steps:")
            print(f"   lamina infrastructure generate --agent {name}")
            print("   lamina docker build")
            print(f"   lamina chat {name}")

            return True

        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            print(f"❌ Error creating agent: {e}")
            return False

    def _generate_agent_config(self, agent_path: Path, config: dict[str, Any]):
        """Generate agent.yaml configuration file"""

        agent_yaml = {
            "name": config["name"],
            "description": config["description"],
            # AI configuration
            "ai_provider": config["ai_provider"],
            "ai_model": config["ai_model"],
            "ai_parameters": config.get("ai_parameters", {}),
            # Memory configuration
            "memory_enabled": config.get("memory_enabled", True),
            "memory_database": config.get("memory_database", "long-term"),
            "memory_embedding_model": config.get("memory_embedding_model", "all-MiniLM-L6-v2"),
            # Personality configuration
            "personality_traits": config.get("personality_traits", []),
            "communication_style": config.get("communication_style", "elegant"),
            "expertise_areas": config.get("expertise_areas", []),
            # Capabilities
            "functions": config.get("functions", []),
            "tools": config.get("tools", []),
            # Constraints
            "constraints": config.get("constraints", ["basic_safety"]),
        }

        with open(agent_path / "agent.yaml", "w") as f:
            yaml.dump(agent_yaml, f, default_flow_style=False, sort_keys=False)

    def _generate_infrastructure_config(self, agent_path: Path, name: str, config: dict[str, Any]):
        """Generate infrastructure.yaml configuration file"""

        infra_yaml = {
            "agent": {"name": name, "display_name": name.title()},
            "container": {
                "image_tag": name,
                "port": 8000,
                "environment": {
                    "AGENT_NAME": name,
                    "AI_PROVIDER": config["ai_provider"],
                    "AI_MODEL": config["ai_model"],
                },
            },
            "resources": {"memory": "1g", "cpu": "0.5", "storage": "1g"},
            "networking": {"expose_port": False, "internal_only": True},
            "security": {"mtls_enabled": True, "certificate_required": True},
        }

        with open(agent_path / "infrastructure.yaml", "w") as f:
            yaml.dump(infra_yaml, f, default_flow_style=False, sort_keys=False)

    def _generate_entities_config(self, agent_path: Path, name: str):
        """Generate known_entities.yaml configuration file"""

        entities_yaml = {
            "entities": {
                "user": {
                    "type": "human",
                    "trust_level": "high",
                    "permissions": ["chat", "query", "memory_access"],
                    "constraints": ["basic_safety", "privacy_protection"],
                },
                "system": {
                    "type": "system",
                    "trust_level": "maximum",
                    "permissions": ["admin", "config", "monitoring"],
                    "constraints": [],
                },
            },
            "groups": {
                "users": {"members": ["user"], "default_permissions": ["chat", "query"]},
                "administrators": {
                    "members": ["system"],
                    "default_permissions": ["admin", "config"],
                },
            },
        }

        with open(agent_path / "known_entities.yaml", "w") as f:
            yaml.dump(entities_yaml, f, default_flow_style=False, sort_keys=False)

    def _generate_ollama_modelfile(self, agent_path: Path, name: str, config: dict[str, Any]):
        """Generate Ollama Modelfile"""

        ollama_dir = agent_path / "ollama"
        ollama_dir.mkdir(exist_ok=True)

        # Extract AI parameters
        ai_params = config.get("ai_parameters", {})
        temperature = ai_params.get("temperature", 0.7)
        top_p = ai_params.get("top_p", 0.9)

        # Build personality description
        traits = ", ".join(config.get("personality_traits", ["helpful", "elegant"]))
        expertise = ", ".join(config.get("expertise_areas", ["general assistance"]))

        modelfile_content = f'''FROM {config["ai_model"]}

PARAMETER temperature {temperature}
PARAMETER top_p {top_p}

SYSTEM """You are {name}, {config["description"]}

Your personality traits include: {traits}

Your areas of expertise: {expertise}

Communication style: {config.get("communication_style", "elegant")}

Please maintain a {config.get("communication_style", "elegant")} tone and be helpful while staying within your defined capabilities and constraints.
"""
'''

        with open(ollama_dir / "Modelfile", "w") as f:
            f.write(modelfile_content)

    def _update_sanctuary_config(self, name: str, config: dict[str, Any]):
        """Update sanctuary configuration to include new agent"""

        # Update sanctuary/system/local.yaml
        local_config_path = self.current_dir / "sanctuary" / "system" / "local.yaml"

        if local_config_path.exists():
            with open(local_config_path) as f:
                local_config = yaml.safe_load(f) or {}
        else:
            local_config = {}

        # Add agent to configuration
        if "agents" not in local_config:
            local_config["agents"] = {}

        local_config["agents"][name] = {
            "enabled": True,
            "template": config.get("template", "conversational"),
            "ai_provider": config["ai_provider"],
            "ai_model": config["ai_model"],
        }

        with open(local_config_path, "w") as f:
            yaml.dump(local_config, f, default_flow_style=False, sort_keys=False)

    def list_agents(self) -> list[str]:
        """List all agents in the current sanctuary"""

        agents_dir = self.current_dir / "sanctuary" / "agents"
        if not agents_dir.exists():
            return []

        agents = []
        for item in agents_dir.iterdir():
            if item.is_dir() and (item / "agent.yaml").exists():
                agents.append(item.name)

        return sorted(agents)

    def get_agent_info(self, name: str) -> dict[str, Any] | None:
        """Get information about a specific agent"""

        agent_path = self.current_dir / "sanctuary" / "agents" / name
        agent_config_path = agent_path / "agent.yaml"

        if not agent_config_path.exists():
            return None

        try:
            with open(agent_config_path) as f:
                config = yaml.safe_load(f)

            # Add additional metadata
            config["path"] = str(agent_path)
            config["has_infrastructure"] = (agent_path / "infrastructure.yaml").exists()
            config["has_entities"] = (agent_path / "known_entities.yaml").exists()

            return config

        except Exception as e:
            logger.error(f"Error reading agent config: {e}")
            return None

    def delete_agent(self, name: str, confirm: bool = False) -> bool:
        """Delete an agent from the sanctuary"""

        agent_path = self.current_dir / "sanctuary" / "agents" / name

        if not agent_path.exists():
            print(f"❌ Agent '{name}' not found")
            return False

        if not confirm:
            response = input(f"❓ Are you sure you want to delete agent '{name}'? (y/N): ")
            if response.lower() != "y":
                print("Cancelled")
                return False

        try:
            # Remove agent directory
            import shutil

            shutil.rmtree(agent_path)

            # Update sanctuary configuration
            local_config_path = self.current_dir / "sanctuary" / "system" / "local.yaml"
            if local_config_path.exists():
                with open(local_config_path) as f:
                    local_config = yaml.safe_load(f) or {}

                if "agents" in local_config and name in local_config["agents"]:
                    del local_config["agents"][name]

                    with open(local_config_path, "w") as f:
                        yaml.dump(local_config, f, default_flow_style=False, sort_keys=False)

            print(f"✅ Agent '{name}' deleted successfully")
            return True

        except Exception as e:
            logger.error(f"Error deleting agent: {e}")
            print(f"❌ Error deleting agent: {e}")
            return False
