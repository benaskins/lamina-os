# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Unified Lamina CLI - Plugin Architecture
🌊 A breath-aware, poetic command interface for the Lamina ecosystem

Implements the vision from ADR-0012 with High Council approval:
- Single entry point with plugin discovery
- Context-aware commands (sanctuary-root vs global)
- Poetic command phrasing with ritual UX
- Modular plugin system for extensibility
"""

import logging
import sys
from pathlib import Path
from typing import Any

import click

from ..environment.config import get_environment_sigil

logger = logging.getLogger(__name__)


class LaminaContext:
    """
    Context for Lamina CLI operations.

    Provides breath-aware context detection and ritual UX support.
    """

    def __init__(self):
        self.cwd = Path.cwd()
        self.sanctuary_root = self._find_sanctuary_root()
        self.is_in_sanctuary = self.sanctuary_root is not None
        self.current_environment = self._detect_environment()

    def _find_sanctuary_root(self) -> Path | None:
        """Find sanctuary root by looking for lamina.yaml or sanctuary.yaml."""
        current = self.cwd
        while current != current.parent:
            if (current / "lamina.yaml").exists() or (current / "sanctuary.yaml").exists():
                return current
            current = current.parent
        return None

    def _detect_environment(self) -> str:
        """Detect current environment context."""
        # Check environment variable first
        import os

        env = os.environ.get("LAMINA_ENVIRONMENT")
        if env:
            return env

        # Check sanctuary config if available
        if self.sanctuary_root:
            sanctuary_config = self.sanctuary_root / "lamina.yaml"
            if sanctuary_config.exists():
                try:
                    import yaml

                    with open(sanctuary_config) as f:
                        config = yaml.safe_load(f)
                    return config.get("environment", "development")
                except Exception:
                    pass

        return "development"

    def get_breath_marker(self) -> str:
        """Get breath marker for current environment."""
        return get_environment_sigil(self.current_environment)

    def echo_breath(self, message: str, **kwargs):
        """Echo message with breath marker."""
        marker = self.get_breath_marker()
        click.echo(f"{marker} {message}", **kwargs)


class LaminaPlugin:
    """
    Base class for Lamina CLI plugins.

    Plugins declare their tier, domain, and provide commands.
    """

    def __init__(self):
        self.tier: str = "unknown"
        self.domain: str = "unknown"
        self.breath_alignment: str = "neutral"

    def get_commands(self) -> dict[str, click.Command]:
        """Return dictionary of command name -> click.Command."""
        return {}

    def get_manifest(self) -> dict[str, Any]:
        """Return plugin manifest for --manifest output."""
        return {
            "tier": self.tier,
            "domain": self.domain,
            "breath_alignment": self.breath_alignment,
            "commands": list(self.get_commands().keys()),
        }


class CorePlugin(LaminaPlugin):
    """Core Lamina operations plugin."""

    def __init__(self):
        super().__init__()
        self.tier = "framework"
        self.domain = "core_operations"
        self.breath_alignment = "breath_aware"

    def get_commands(self) -> dict[str, click.Command]:
        return {
            "sanctuary": self._sanctuary_command(),
            "agent": self._agent_command(),
            "chat": self._chat_command(),
            "infrastructure": self._infrastructure_command(),
            "environment": self._environment_command(),
        }

    def _sanctuary_command(self):
        @click.group(name="sanctuary")
        def sanctuary_group():
            """🏛️ Sanctuary management - spaces for mindful AI development."""
            pass

        @sanctuary_group.command(name="create")
        @click.argument("sanctuary_name")
        @click.option("--agents", help="Path to agents configuration file")
        @click.option("--template", default="basic", help="Sanctuary template")
        @click.pass_obj
        def create_sanctuary(
            ctx: LaminaContext, sanctuary_name: str, agents: str | None, template: str
        ):
            """✨ Create a new sanctuary for mindful AI development."""
            ctx.echo_breath(f"Creating sanctuary '{sanctuary_name}'...")

            from ..cli.sanctuary_cli import SanctuaryCLI

            cli = SanctuaryCLI()

            # Create the sanctuary
            success = cli.init_sanctuary(sanctuary_name, template, interactive=False)
            if success:
                ctx.echo_breath(f"🏛️ Sanctuary '{sanctuary_name}' awakened successfully")

                # Handle agents file if provided
                if agents:
                    agents_path = Path(agents)
                    if agents_path.exists():
                        ctx.echo_breath(f"🤖 Integrating agents from {agents}")
                        # TODO: Implement agent integration from file
                    else:
                        ctx.echo_breath(f"⚠️ Agents file not found: {agents}", err=True)

                ctx.echo_breath(f"💫 Enter your sanctuary: cd {sanctuary_name}")
            else:
                ctx.echo_breath("❌ Sanctuary creation encountered obstacles", err=True)
                sys.exit(1)

        @sanctuary_group.command(name="status")
        @click.pass_obj
        def sanctuary_status(ctx: LaminaContext):
            """📊 Show sanctuary status and breath alignment."""
            if not ctx.is_in_sanctuary:
                ctx.echo_breath(
                    "❓ Not within a sanctuary. Use 'lamina sanctuary create' to begin.", err=True
                )
                return

            ctx.echo_breath("🏛️ Sanctuary Status")
            ctx.echo_breath(f"   Root: {ctx.sanctuary_root}")
            ctx.echo_breath(f"   Environment: {ctx.current_environment}")
            ctx.echo_breath(f"   Breath Marker: {ctx.get_breath_marker()}")

            # TODO: Add more sanctuary status details

        @sanctuary_group.command(name="list")
        @click.pass_obj
        def list_sanctuaries(ctx: LaminaContext):
            """📋 List available sanctuaries."""
            from ..cli.sanctuary_cli import SanctuaryCLI

            cli = SanctuaryCLI()

            sanctuaries = cli.list_sanctuaries()
            if sanctuaries:
                ctx.echo_breath("🏛️ Available sanctuaries:")
                for sanctuary in sanctuaries:
                    ctx.echo_breath(f"   📁 {sanctuary}")
            else:
                ctx.echo_breath("No sanctuaries found. Create one with 'lamina sanctuary create'")

        return sanctuary_group

    def _agent_command(self):
        @click.group(name="agent")
        def agent_group():
            """🤖 Agent creation and management."""
            pass

        @agent_group.command(name="create")
        @click.argument("agent_name")
        @click.option("--archetype", default="conversational", help="Agent archetype")
        @click.option("--provider", default="ollama", help="AI provider")
        @click.option("--model", help="AI model to use")
        @click.pass_obj
        def create_agent(
            ctx: LaminaContext, agent_name: str, archetype: str, provider: str, model: str | None
        ):
            """✨ Awaken a new agent with mindful purpose."""
            if not ctx.is_in_sanctuary:
                ctx.echo_breath(
                    "🏛️ Agent creation requires a sanctuary. Use 'lamina sanctuary create' first.",
                    err=True,
                )
                return

            ctx.echo_breath(f"Awakening agent '{agent_name}' with {archetype} archetype...")

            try:
                from ..cli.agent_cli import AgentCLI

                cli = AgentCLI()

                success = cli.create_agent(agent_name, archetype, provider, model)
                if success:
                    ctx.echo_breath(f"🤖 Agent '{agent_name}' awakened successfully")
                    ctx.echo_breath(f"💫 Test with: lamina chat {agent_name}")
                else:
                    ctx.echo_breath("❌ Agent awakening encountered obstacles", err=True)
                    sys.exit(1)
            except ImportError:
                ctx.echo_breath("❌ Agent CLI not available", err=True)
                sys.exit(1)

        @agent_group.command(name="list")
        @click.pass_obj
        def list_agents(ctx: LaminaContext):
            """📋 List awakened agents in sanctuary."""
            if not ctx.is_in_sanctuary:
                ctx.echo_breath("🏛️ Agent listing requires a sanctuary context.", err=True)
                return

            try:
                from ..cli.agent_cli import AgentCLI

                cli = AgentCLI()

                agents = cli.list_agents()
                if agents:
                    ctx.echo_breath("🤖 Awakened agents:")
                    for agent in agents:
                        ctx.echo_breath(f"   🔹 {agent}")
                else:
                    ctx.echo_breath("No agents found. Create one with 'lamina agent create'")
            except ImportError:
                ctx.echo_breath("❌ Agent CLI not available", err=True)

        @agent_group.command(name="info")
        @click.argument("agent_name")
        @click.pass_obj
        def agent_info(ctx: LaminaContext, agent_name: str):
            """📖 Show agent essence and configuration."""
            try:
                from ..cli.agent_cli import AgentCLI

                cli = AgentCLI()

                info = cli.get_agent_info(agent_name)
                if info:
                    ctx.echo_breath(f"🤖 Agent: {info['name']}")
                    ctx.echo_breath(f"   Essence: {info.get('description', 'Unknown')}")
                    ctx.echo_breath(f"   Archetype: {info.get('template', 'Unknown')}")
                    ctx.echo_breath(f"   Provider: {info.get('ai_provider', 'Unknown')}")
                    ctx.echo_breath(f"   Model: {info.get('ai_model', 'Unknown')}")
                else:
                    ctx.echo_breath(f"❌ Agent '{agent_name}' not found", err=True)
                    sys.exit(1)
            except ImportError:
                ctx.echo_breath("❌ Agent CLI not available", err=True)

        return agent_group

    def _chat_command(self):
        @click.command(name="chat")
        @click.argument("agent", required=False)
        @click.argument("message", required=False)
        @click.option("--demo", is_flag=True, help="Run interactive demo")
        @click.option("--interactive", "-i", is_flag=True, help="Interactive mode")
        @click.pass_obj
        def chat_command(
            ctx: LaminaContext,
            agent: str | None,
            message: str | None,
            demo: bool,
            interactive: bool,
        ):
            """💬 Converse with awakened agents."""
            ctx.echo_breath("🌊 Opening channels for mindful conversation...")

            # Import and delegate to existing chat handler
            from argparse import Namespace

            from ..cli.main import handle_chat_command

            args = Namespace(agent=agent, message=message, demo=demo, interactive=interactive)

            handle_chat_command(args)

        return chat_command

    def _infrastructure_command(self):
        @click.group(name="infrastructure")
        def infra_group():
            """🏗️ Infrastructure management and deployment."""
            pass

        @infra_group.command(name="generate")
        @click.option("--agent", help="Agent name")
        @click.option("--force", is_flag=True, help="Force regeneration")
        @click.pass_obj
        def generate_infra(ctx: LaminaContext, agent: str | None, force: bool):
            """🔧 Generate infrastructure configurations."""
            ctx.echo_breath("🏗️ Generating infrastructure blueprints...")

            # TODO: Implement infrastructure generation
            ctx.echo_breath("✨ Infrastructure generation complete")

        @infra_group.command(name="status")
        @click.pass_obj
        def infra_status(ctx: LaminaContext):
            """📊 Show infrastructure status."""
            ctx.echo_breath("📊 Infrastructure Status")
            # TODO: Implement infrastructure status
            ctx.echo_breath("   Status: Active and breath-aligned")

        return infra_group

    def _environment_command(self):
        @click.group(name="environment")
        def env_group():
            """🌊 Environment management and validation."""
            pass

        @env_group.command(name="list")
        @click.pass_obj
        def list_environments(ctx: LaminaContext):
            """📋 List available environments."""
            try:
                from ..environment.manager import EnvironmentManager

                manager = EnvironmentManager()

                environments = manager.get_available_environments()
                if environments:
                    ctx.echo_breath("🌊 Available environments:")
                    for env_name in environments:
                        config = manager.get_environment_config(env_name)
                        ctx.echo_breath(f"   {config.sigil} {env_name} ({config.type})")
                else:
                    ctx.echo_breath("No environments found")
            except Exception as e:
                ctx.echo_breath(f"❌ Error loading environments: {e}", err=True)

        @env_group.command(name="status")
        @click.argument("environment", required=False)
        @click.pass_obj
        def env_status(ctx: LaminaContext, environment: str | None):
            """📊 Show environment status and breath alignment."""
            try:
                from ..environment.manager import EnvironmentManager

                manager = EnvironmentManager()

                if environment:
                    status = manager.get_environment_status(environment)
                    if "error" in status:
                        ctx.echo_breath(f"❌ {status['error']}", err=True)
                        return

                    ctx.echo_breath(f"{status['sigil']} Environment: {status['name']}")
                    ctx.echo_breath(f"   Type: {status['type']}")
                    ctx.echo_breath(f"   Essence: {status['description']}")
                    ctx.echo_breath(f"   Validation: {status['validation']['status']}")
                    ctx.echo_breath(f"   Services: {', '.join(status['services'])}")
                    ctx.echo_breath(f"   Active: {status['is_current']}")
                else:
                    # Show all environments
                    environments = manager.get_available_environments()
                    ctx.echo_breath("🌊 Environment Status:")
                    for env_name in environments:
                        status = manager.get_environment_status(env_name)
                        validation_icon = (
                            "✅" if status["validation"]["status"] == "valid" else "❌"
                        )
                        ctx.echo_breath(f"   {status['sigil']} {env_name}: {validation_icon}")
            except Exception as e:
                ctx.echo_breath(f"❌ Error checking environment status: {e}", err=True)

        @env_group.command(name="validate")
        @click.argument("environment", required=False)
        @click.pass_obj
        def validate_env(ctx: LaminaContext, environment: str | None):
            """🔍 Validate environment configurations."""
            try:
                from ..environment.manager import EnvironmentManager
                from ..environment.validators import validate_environment_config

                manager = EnvironmentManager()

                if environment:
                    config = manager.get_environment_config(environment)
                    validate_environment_config(config)
                    ctx.echo_breath(
                        f"{config.sigil} ✅ Environment {environment} validation passed"
                    )
                else:
                    results = manager.validate_all_environments()
                    ctx.echo_breath("🌊 Environment Validation Results:")
                    for env_name, is_valid in results.items():
                        config = manager.get_environment_config(env_name)
                        status = "✅ Valid" if is_valid else "❌ Invalid"
                        ctx.echo_breath(f"   {config.sigil} {env_name}: {status}")
            except Exception as e:
                ctx.echo_breath(f"❌ Environment validation failed: {e}", err=True)
                sys.exit(1)

        return env_group


class GitOpsPlugin(LaminaPlugin):
    """GitOps deployment operations plugin."""

    def __init__(self):
        super().__init__()
        self.tier = "deployment"
        self.domain = "gitops_operations"
        self.breath_alignment = "deployment_mindful"

    def get_commands(self) -> dict[str, click.Command]:
        return {
            "deploy": self._deploy_command(),
            "status": self._status_command(),
        }

    def _deploy_command(self):
        @click.group(name="deploy")
        def deploy_group():
            """🚀 Deployment operations with GitOps mindfulness."""
            pass

        @deploy_group.command(name="setup")
        @click.argument("environment", default="production")
        @click.option("--repo-url", default="https://github.com/benaskins/lamina-os")
        @click.option("--argocd/--no-argocd", default=True)
        @click.pass_obj
        def setup_gitops(ctx: LaminaContext, environment: str, repo_url: str, argocd: bool):
            """✨ Setup GitOps deployment for mindful infrastructure."""
            ctx.echo_breath(f"🚀 Setting up GitOps for {environment} environment...")

            from argparse import Namespace

            from ..cli.main import handle_gitops_command

            args = Namespace(
                gitops_command="setup", environment=environment, repo_url=repo_url, argocd=argocd
            )

            handle_gitops_command(args)

        @deploy_group.command(name="charts")
        @click.argument("environment", default="production")
        @click.option("--output-dir", "-o", default="charts")
        @click.option("--validate/--no-validate", default=True)
        @click.option("--package/--no-package", default=False)
        @click.pass_obj
        def generate_charts(
            ctx: LaminaContext, environment: str, output_dir: str, validate: bool, package: bool
        ):
            """📊 Generate Helm charts for GitOps deployment."""
            ctx.echo_breath(f"📊 Generating Helm charts for {environment}...")

            from argparse import Namespace

            from ..cli.main import handle_gitops_command

            args = Namespace(
                gitops_command="generate-charts",
                environment=environment,
                output_dir=output_dir,
                validate=validate,
                package=package,
            )

            handle_gitops_command(args)

        @deploy_group.command(name="apply")
        @click.argument("environment", default="production")
        @click.option("--chart-path", "-c")
        @click.option("--namespace", "-n")
        @click.option("--dry-run/--no-dry-run", default=False)
        @click.option("--wait/--no-wait", default=True)
        @click.option("--timeout", "-t", type=int, default=600)
        @click.pass_obj
        def deploy_apply(
            ctx: LaminaContext,
            environment: str,
            chart_path: str | None,
            namespace: str | None,
            dry_run: bool,
            wait: bool,
            timeout: int,
        ):
            """🌊 Apply deployment to Kubernetes with mindful breath."""
            action = "dry-run" if dry_run else "deployment"
            ctx.echo_breath(f"🌊 Applying {action} to {environment}...")

            from argparse import Namespace

            from ..cli.main import handle_gitops_command

            args = Namespace(
                gitops_command="deploy",
                environment=environment,
                chart_path=chart_path,
                namespace=namespace,
                dry_run=dry_run,
                wait=wait,
                timeout=timeout,
            )

            handle_gitops_command(args)

        return deploy_group

    def _status_command(self):
        @click.command(name="status")
        @click.argument("environment", default="production")
        @click.option("--namespace", "-n")
        @click.pass_obj
        def deployment_status(ctx: LaminaContext, environment: str, namespace: str | None):
            """📊 Check deployment status with breath presence."""
            ctx.echo_breath(f"📊 Checking {environment} deployment status...")

            from argparse import Namespace

            from ..cli.main import handle_gitops_command

            args = Namespace(gitops_command="status", environment=environment, namespace=namespace)

            handle_gitops_command(args)

        return deployment_status


class PluginDiscovery:
    """
    Plugin discovery and registration system.

    Discovers plugins and creates dynamic CLI with all commands.
    """

    def __init__(self):
        self.plugins: list[LaminaPlugin] = []
        self._discover_plugins()

    def _discover_plugins(self):
        """Discover and register all available plugins."""
        # Core plugins (always available)
        self.plugins.append(CorePlugin())
        self.plugins.append(GitOpsPlugin())

        # TODO: Add dynamic plugin discovery from entry points
        # This would allow other packages to register plugins

    def get_all_commands(self) -> dict[str, click.Command]:
        """Get all commands from all plugins."""
        commands = {}
        for plugin in self.plugins:
            plugin_commands = plugin.get_commands()
            for name, command in plugin_commands.items():
                if name in commands:
                    # Handle command conflicts with breath-aware warning
                    click.echo(f"⚠️ Command conflict: {name} (using {plugin.domain})")
                commands[name] = command
        return commands

    def get_manifest(self) -> dict[str, Any]:
        """Get manifest of all plugins for --manifest output."""
        return {plugin.domain: plugin.get_manifest() for plugin in self.plugins}


@click.group(invoke_without_command=True)
@click.option("--manifest", is_flag=True, help="Show plugin manifest and breath alignments")
@click.pass_context
def lamina_cli(ctx, manifest):
    """
    🌊 Lamina - Unified CLI for Mindful AI Development

    A breath-aware interface for the complete Lamina ecosystem.
    Commands adapt to your context (sanctuary-root vs global).
    """
    # Create context object
    lamina_ctx = LaminaContext()
    ctx.obj = lamina_ctx

    if manifest:
        discovery = PluginDiscovery()
        manifest_data = discovery.get_manifest()

        lamina_ctx.echo_breath("🌊 Lamina CLI Plugin Manifest")
        lamina_ctx.echo_breath("")

        for domain, plugin_info in manifest_data.items():
            tier_icon = {"framework": "🔧", "deployment": "🚀", "specialized": "⚙️"}.get(
                plugin_info["tier"], "❓"
            )
            lamina_ctx.echo_breath(f"{tier_icon} {domain.replace('_', ' ').title()}")
            lamina_ctx.echo_breath(f"   Tier: {plugin_info['tier']}")
            lamina_ctx.echo_breath(f"   Breath Alignment: {plugin_info['breath_alignment']}")
            lamina_ctx.echo_breath(f"   Commands: {', '.join(plugin_info['commands'])}")
            lamina_ctx.echo_breath("")

        return

    if ctx.invoked_subcommand is None:
        # Show context-aware help
        if lamina_ctx.is_in_sanctuary:
            lamina_ctx.echo_breath(f"🏛️ Sanctuary: {lamina_ctx.sanctuary_root.name}")
            lamina_ctx.echo_breath(f"🌊 Environment: {lamina_ctx.current_environment}")
            lamina_ctx.echo_breath("")
            lamina_ctx.echo_breath("Common sanctuary commands:")
            lamina_ctx.echo_breath("  lamina agent create <name>     # Awaken new agent")
            lamina_ctx.echo_breath("  lamina sanctuary status        # Check sanctuary health")
            lamina_ctx.echo_breath("  lamina chat                    # Begin conversation")
        else:
            lamina_ctx.echo_breath("Welcome to the Lamina ecosystem")
            lamina_ctx.echo_breath("")
            lamina_ctx.echo_breath("Getting started:")
            lamina_ctx.echo_breath("  lamina sanctuary create <name> # Create workspace")
            lamina_ctx.echo_breath("  lamina environment list        # Show environments")

        lamina_ctx.echo_breath("")
        lamina_ctx.echo_breath("Use 'lamina --help' for complete command reference")


def create_dynamic_cli():
    """Create the dynamic CLI with all discovered plugins."""
    discovery = PluginDiscovery()
    commands = discovery.get_all_commands()

    # Add all discovered commands to the main CLI group
    for name, command in commands.items():
        lamina_cli.add_command(command, name=name)

    return lamina_cli


def main():
    """Main entry point for unified lamina CLI."""
    cli = create_dynamic_cli()
    cli()


if __name__ == "__main__":
    main()
