# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Sanctuary CLI - Sanctuary Management and Scaffolding

Command-line interface for creating, managing, and configuring
agent sanctuaries with elegant templates.
"""

import argparse
import logging
from pathlib import Path
from typing import Any

import yaml

from lamina.cli.templates import AGENT_TEMPLATES

logger = logging.getLogger(__name__)


class SanctuaryCLI:
    """Command-line interface for sanctuary management"""

    def __init__(self):
        self.current_dir = Path.cwd()

    def init_sanctuary(self, name: str, template: str = "basic", interactive: bool = True) -> bool:
        """
        Initialize a new sanctuary with scaffolding.

        Args:
            name: Name of the sanctuary
            template: Template type (basic, advanced, custom)
            interactive: Whether to use interactive prompts

        Returns:
            True if successful, False otherwise
        """
        try:
            sanctuary_path = self.current_dir / name

            if sanctuary_path.exists():
                print(f"❌ Directory '{name}' already exists")
                return False

            print(f"🏗️  Creating sanctuary: {name}")

            # Create directory structure
            self._create_directory_structure(sanctuary_path, template)

            # Get configuration from user
            if interactive:
                config = self._get_interactive_config(template)
            else:
                config = self._get_default_config(template)

            # Generate configuration files
            self._generate_config_files(sanctuary_path, config)

            # Generate initial agents if specified
            if config.get("initial_agents"):
                self._create_initial_agents(sanctuary_path, config["initial_agents"])

            print(f"✅ Sanctuary '{name}' created successfully!")
            print(f"📁 Location: {sanctuary_path}")
            print("\n📋 Next steps:")
            print(f"   cd {name}")
            print("   lamina agent create <agent-name> --template=<template>")
            print("   lamina infrastructure generate")
            print("   lamina docker up")

            return True

        except Exception as e:
            logger.error(f"Failed to create sanctuary: {e}")
            print(f"❌ Error creating sanctuary: {e}")
            return False

    def _create_directory_structure(self, sanctuary_path: Path, template: str):
        """Create the basic directory structure"""

        directories = [
            "sanctuary/agents",
            "sanctuary/system",
            "sanctuary/vows",
            "config",
            "infrastructure",
            "logs",
        ]

        if template == "advanced":
            directories.extend(["sanctuary/houses", "sanctuary/essence", "sanctuary/modulation"])

        for directory in directories:
            (sanctuary_path / directory).mkdir(parents=True, exist_ok=True)

    def _get_interactive_config(self, template: str) -> dict[str, Any]:
        """Get configuration through interactive prompts"""

        config = {}

        print("\n🔧 Sanctuary Configuration")
        print("=" * 40)

        # Basic configuration
        config["description"] = input("Description (optional): ").strip() or "AI Agent Sanctuary"

        # AI provider selection
        print("\n🤖 AI Provider:")
        print("1. Ollama (local, privacy-focused)")
        print("2. HuggingFace (local, flexible)")
        provider_choice = input("Choose provider [1-2] (default: 1): ").strip() or "1"

        provider_map = {"1": "ollama", "2": "huggingface"}
        config["ai_provider"] = provider_map.get(provider_choice, "ollama")

        # Model selection based on provider
        if config["ai_provider"] == "ollama":
            default_model = "llama3.2:3b"
            config["ai_model"] = (
                input(f"Model (default: {default_model}): ").strip() or default_model
            )
        else:
            default_model = "microsoft/DialoGPT-medium"
            config["ai_model"] = (
                input(f"Model (default: {default_model}): ").strip() or default_model
            )

        # Initial agents
        print("\n👥 Initial Agents:")
        print("Available templates: conversational, analytical, security, reasoning")
        agents_input = input("Agent names (comma-separated, optional): ").strip()

        if agents_input:
            agent_names = [name.strip() for name in agents_input.split(",")]
            config["initial_agents"] = []

            for agent_name in agent_names:
                print(f"\n🤖 Configuring agent: {agent_name}")
                agent_template = input("Template [conversational]: ").strip() or "conversational"
                config["initial_agents"].append({"name": agent_name, "template": agent_template})

        return config

    def _get_default_config(self, template: str) -> dict[str, Any]:
        """Get default configuration for non-interactive mode"""

        return {
            "description": "AI Agent Sanctuary",
            "ai_provider": "ollama",
            "ai_model": "llama3.2:3b",
            "initial_agents": (
                [{"name": "assistant", "template": "conversational"}] if template == "basic" else []
            ),
        }

    def _generate_config_files(self, sanctuary_path: Path, config: dict[str, Any]):
        """Generate configuration files"""

        # lamina.yaml - Project configuration
        lamina_config = {
            "name": sanctuary_path.name,
            "description": config["description"],
            "version": "1.0.0",
            "ai_provider": config["ai_provider"],
            "ai_model": config["ai_model"],
            "created_with": "lamina-core",
        }

        with open(sanctuary_path / "lamina.yaml", "w") as f:
            yaml.dump(lamina_config, f, default_flow_style=False)

        # config/system.yaml - System configuration
        system_config = {
            "system": {
                "name": sanctuary_path.name,
                "description": config["description"],
                "ai_provider": config["ai_provider"],
                "ai_model": config["ai_model"],
            },
            "infrastructure": {
                "docker_enabled": True,
                "mtls_enabled": True,
                "observability_enabled": True,
            },
            "memory": {
                "enabled": True,
                "backend": "chromadb",
                "embedding_model": "all-MiniLM-L6-v2",
            },
        }

        with open(sanctuary_path / "config" / "system.yaml", "w") as f:
            yaml.dump(system_config, f, default_flow_style=False)

        # config/infrastructure.yaml - Infrastructure configuration
        infra_config = {
            "infrastructure": {
                "docker": {
                    "compose_version": "3.8",
                    "network_name": f"{sanctuary_path.name}_network",
                },
                "nginx": {"enabled": True, "port": 443, "mtls_enabled": True},
                "observability": {
                    "grafana_enabled": True,
                    "loki_enabled": True,
                    "vector_enabled": True,
                },
            }
        }

        with open(sanctuary_path / "config" / "infrastructure.yaml", "w") as f:
            yaml.dump(infra_config, f, default_flow_style=False)

        # sanctuary/system/local.yaml - Local system config
        local_config = {
            "agents": {},
            "coordination": {"enabled": True, "coordinator_agent": "coordinator"},
            "constraints": {
                "basic_safety": True,
                "privacy_protection": True,
                "security_review": True,
            },
        }

        with open(sanctuary_path / "sanctuary" / "system" / "local.yaml", "w") as f:
            yaml.dump(local_config, f, default_flow_style=False)

        # Create basic vow file
        basic_vow = """# Basic Constraints

## Safety Constraints
- No harmful or dangerous instructions
- No personal attacks or harassment
- Respect user privacy and data protection

## Operational Constraints
- Maintain elegant communication
- Stay within defined capabilities
- Apply security validation when needed

## Ethical Guidelines
- Treat all users with respect
- Avoid bias and discrimination
- Be honest about limitations
"""

        with open(sanctuary_path / "sanctuary" / "vows" / "basic_constraints.md", "w") as f:
            f.write(basic_vow)

    def _create_initial_agents(self, sanctuary_path: Path, agents: list[dict[str, str]]):
        """Create initial agents from configuration"""

        for agent_config in agents:
            agent_name = agent_config["name"]
            template = agent_config["template"]

            print(f"   🤖 Creating agent: {agent_name} ({template})")

            agent_path = sanctuary_path / "sanctuary" / "agents" / agent_name
            agent_path.mkdir(parents=True, exist_ok=True)

            # Generate agent.yaml from template
            if template in AGENT_TEMPLATES:
                agent_yaml = AGENT_TEMPLATES[template].copy()
                agent_yaml["name"] = agent_name

                with open(agent_path / "agent.yaml", "w") as f:
                    yaml.dump(agent_yaml, f, default_flow_style=False)

            # Create infrastructure.yaml
            infra_yaml = {
                "agent": {"name": agent_name, "display_name": agent_name.title()},
                "container": {"image_tag": agent_name, "port": 8000},
                "resources": {"memory": "1g", "cpu": "0.5"},
            }

            with open(agent_path / "infrastructure.yaml", "w") as f:
                yaml.dump(infra_yaml, f, default_flow_style=False)

            # Create known_entities.yaml
            entities_yaml = {
                "entities": {
                    "user": {
                        "type": "human",
                        "trust_level": "high",
                        "permissions": ["chat", "query"],
                    }
                }
            }

            with open(agent_path / "known_entities.yaml", "w") as f:
                yaml.dump(entities_yaml, f, default_flow_style=False)

            # Create Ollama Modelfile if using Ollama
            ollama_dir = agent_path / "ollama"
            ollama_dir.mkdir(exist_ok=True)

            modelfile_content = f"""FROM llama3.2:3b

PARAMETER temperature 0.7
PARAMETER top_p 0.9

SYSTEM \"\"\"You are {agent_name}, a helpful AI assistant.

{AGENT_TEMPLATES.get(template, {}).get('description', 'An elegant AI assistant.')}

Personality traits: {', '.join(AGENT_TEMPLATES.get(template, {}).get('personality_traits', ['helpful', 'elegant']))}

Maintain a {AGENT_TEMPLATES.get(template, {}).get('communication_style', 'elegant')} communication style.
\"\"\"
"""

            with open(ollama_dir / "Modelfile", "w") as f:
                f.write(modelfile_content)

    def list_sanctuaries(self) -> list[str]:
        """List available sanctuaries in current directory"""

        sanctuaries = []
        for item in self.current_dir.iterdir():
            if item.is_dir() and (item / "lamina.yaml").exists():
                sanctuaries.append(item.name)

        return sanctuaries

    def sanctuary_status(self, sanctuary_path: str | None = None) -> dict[str, Any]:
        """Get status of a sanctuary"""

        if sanctuary_path:
            path = Path(sanctuary_path)
        else:
            path = self.current_dir

        if not (path / "lamina.yaml").exists():
            return {"error": "Not a lamina sanctuary"}

        # Read configuration
        with open(path / "lamina.yaml") as f:
            config = yaml.safe_load(f)

        # Count agents
        agents_dir = path / "sanctuary" / "agents"
        agent_count = (
            len([d for d in agents_dir.iterdir() if d.is_dir()]) if agents_dir.exists() else 0
        )

        # Check for infrastructure
        has_infrastructure = (path / "config" / "infrastructure.yaml").exists()

        return {
            "name": config.get("name", "Unknown"),
            "description": config.get("description", ""),
            "ai_provider": config.get("ai_provider", "unknown"),
            "agent_count": agent_count,
            "has_infrastructure": has_infrastructure,
            "path": str(path),
        }


def main():
    """Main CLI entry point for sanctuary management"""
    parser = argparse.ArgumentParser(description="Lamina Sanctuary Management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize new sanctuary")
    init_parser.add_argument("name", help="Sanctuary name")
    init_parser.add_argument(
        "--template",
        choices=["basic", "advanced", "custom"],
        default="basic",
        help="Sanctuary template",
    )
    init_parser.add_argument(
        "--non-interactive", action="store_true", help="Use default configuration"
    )

    # List command
    subparsers.add_parser("list", help="List sanctuaries")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show sanctuary status")
    status_parser.add_argument("--path", help="Sanctuary path")

    args = parser.parse_args()

    cli = SanctuaryCLI()

    if args.command == "init":
        cli.init_sanctuary(args.name, args.template, not args.non_interactive)

    elif args.command == "list":
        sanctuaries = cli.list_sanctuaries()
        if sanctuaries:
            print("Available sanctuaries:")
            for sanctuary in sanctuaries:
                print(f"  📁 {sanctuary}")
        else:
            print("No sanctuaries found in current directory")

    elif args.command == "status":
        status = cli.sanctuary_status(args.path)
        if "error" in status:
            print(f"❌ {status['error']}")
        else:
            print("📊 Sanctuary Status")
            print(f"Name: {status['name']}")
            print(f"Description: {status['description']}")
            print(f"AI Provider: {status['ai_provider']}")
            print(f"Agents: {status['agent_count']}")
            print(f"Infrastructure: {'✅' if status['has_infrastructure'] else '❌'}")
            print(f"Path: {status['path']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
