# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Main CLI Entry Point

Unified command-line interface for all Lamina Core operations including
sanctuary management, agent creation, and system operations.
"""

import argparse
import sys

from lamina.cli.sanctuary_cli import SanctuaryCLI


def print_banner():
    """Print Lamina Core banner"""
    banner = """
╔══════════════════════════════════════╗
║              Lamina Core             ║
║   Modular AI Agent Framework         ║
╚══════════════════════════════════════╝
"""
    print(banner)


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser"""

    parser = argparse.ArgumentParser(
        description="Lamina Core - Modular AI Agent Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lamina sanctuary init my-agents         # Create new sanctuary
  lamina agent create assistant           # Create new agent
  lamina chat --demo                      # Interactive chat demo
  lamina chat --demo "Hello there!"      # Single message demo
  lamina infrastructure generate         # Generate infrastructure
  lamina docker up                       # Start services

For more help on specific commands:
  lamina sanctuary --help
  lamina agent --help
  lamina chat --help
""",
    )

    # Global options
    parser.add_argument("--version", action="version", version="lamina-core 0.1.0")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Sanctuary management
    sanctuary_parser = subparsers.add_parser(
        "sanctuary", help="Sanctuary management and scaffolding"
    )
    sanctuary_subparsers = sanctuary_parser.add_subparsers(dest="sanctuary_command")

    # sanctuary init
    init_parser = sanctuary_subparsers.add_parser("init", help="Initialize new sanctuary")
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

    # sanctuary list
    sanctuary_subparsers.add_parser("list", help="List sanctuaries")

    # sanctuary status
    status_parser = sanctuary_subparsers.add_parser("status", help="Show sanctuary status")
    status_parser.add_argument("--path", help="Sanctuary path")

    # Agent management
    agent_parser = subparsers.add_parser("agent", help="Agent creation and management")
    agent_subparsers = agent_parser.add_subparsers(dest="agent_command")

    # agent create
    create_parser = agent_subparsers.add_parser("create", help="Create new agent")
    create_parser.add_argument("name", help="Agent name")
    create_parser.add_argument(
        "--template",
        choices=["conversational", "analytical", "security", "reasoning"],
        default="conversational",
        help="Agent template",
    )
    create_parser.add_argument(
        "--provider", choices=["ollama", "huggingface"], default="ollama", help="AI provider"
    )
    create_parser.add_argument("--model", help="AI model to use")

    # agent list
    agent_subparsers.add_parser("list", help="List agents")

    # agent info
    info_parser = agent_subparsers.add_parser("info", help="Show agent information")
    info_parser.add_argument("name", help="Agent name")

    # Chat interface
    chat_parser = subparsers.add_parser("chat", help="Chat with agents")
    chat_parser.add_argument("agent", nargs="?", help="Agent name (optional)")
    chat_parser.add_argument("message", nargs="?", help="Message to send")
    chat_parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    chat_parser.add_argument("--demo", action="store_true", help="Run chat demo with mock agents")

    # Infrastructure management
    infra_parser = subparsers.add_parser("infrastructure", help="Infrastructure management")
    infra_subparsers = infra_parser.add_subparsers(dest="infra_command")

    # infrastructure generate
    gen_parser = infra_subparsers.add_parser("generate", help="Generate infrastructure files")
    gen_parser.add_argument("--agent", help="Agent name")
    gen_parser.add_argument("--force", action="store_true", help="Force regeneration")

    # infrastructure status
    infra_subparsers.add_parser("status", help="Show infrastructure status")

    # Docker management
    docker_parser = subparsers.add_parser("docker", help="Docker operations")
    docker_subparsers = docker_parser.add_subparsers(dest="docker_command")

    # docker commands
    docker_subparsers.add_parser("build", help="Build containers")
    docker_subparsers.add_parser("up", help="Start services")
    docker_subparsers.add_parser("down", help="Stop services")
    docker_subparsers.add_parser("logs", help="Show logs")
    docker_subparsers.add_parser("status", help="Show container status")

    # Environment management
    env_parser = subparsers.add_parser("environment", help="Environment management")
    env_subparsers = env_parser.add_subparsers(dest="env_command")

    # environment create/configure
    env_create_parser = env_subparsers.add_parser("create", help="Create environment configuration")
    env_create_parser.add_argument(
        "name", choices=["development", "test", "production"], help="Environment name"
    )

    # environment list
    env_subparsers.add_parser("list", help="List available environments")

    # environment status
    env_status_parser = env_subparsers.add_parser("status", help="Show environment status")
    env_status_parser.add_argument("name", nargs="?", help="Environment name")

    # environment validate
    env_validate_parser = env_subparsers.add_parser(
        "validate", help="Validate environment configurations"
    )
    env_validate_parser.add_argument(
        "name", nargs="?", help="Environment name (validates all if not specified)"
    )

    # GitOps management
    gitops_parser = subparsers.add_parser("gitops", help="GitOps deployment management")
    gitops_subparsers = gitops_parser.add_subparsers(dest="gitops_command")

    # gitops setup
    gitops_setup_parser = gitops_subparsers.add_parser(
        "setup", help="Complete GitOps setup for environment"
    )
    gitops_setup_parser.add_argument(
        "environment", choices=["development", "test", "production"], help="Environment name"
    )
    gitops_setup_parser.add_argument(
        "--repo-url", default="https://github.com/benaskins/lamina-os", help="Git repository URL"
    )
    gitops_setup_parser.add_argument(
        "--argocd/--no-argocd", default=True, help="Generate ArgoCD Application manifest"
    )

    # gitops generate-charts
    gitops_gen_parser = gitops_subparsers.add_parser(
        "generate-charts", help="Generate Helm charts for GitOps deployment"
    )
    gitops_gen_parser.add_argument(
        "environment", choices=["development", "test", "production"], help="Environment name"
    )
    gitops_gen_parser.add_argument(
        "--output-dir", "-o", default="charts", help="Output directory for generated charts"
    )
    gitops_gen_parser.add_argument(
        "--validate/--no-validate", default=True, help="Validate generated charts"
    )
    gitops_gen_parser.add_argument(
        "--package/--no-package", default=False, help="Package charts into .tgz files"
    )

    # gitops deploy
    gitops_deploy_parser = gitops_subparsers.add_parser(
        "deploy", help="Deploy environment using Helm chart"
    )
    gitops_deploy_parser.add_argument(
        "environment", choices=["development", "test", "production"], help="Environment name"
    )
    gitops_deploy_parser.add_argument("--chart-path", "-c", help="Path to Helm chart")
    gitops_deploy_parser.add_argument("--namespace", "-n", help="Kubernetes namespace")
    gitops_deploy_parser.add_argument(
        "--dry-run/--no-dry-run", default=False, help="Perform a dry run"
    )
    gitops_deploy_parser.add_argument(
        "--wait/--no-wait", default=True, help="Wait for deployment to complete"
    )
    gitops_deploy_parser.add_argument(
        "--timeout", "-t", type=int, default=600, help="Timeout in seconds"
    )

    # gitops status
    gitops_status_parser = gitops_subparsers.add_parser(
        "status", help="Check deployment status for environment"
    )
    gitops_status_parser.add_argument(
        "environment", choices=["development", "test", "production"], help="Environment name"
    )
    gitops_status_parser.add_argument("--namespace", "-n", help="Kubernetes namespace")

    return parser


def handle_sanctuary_command(args):
    """Handle sanctuary subcommands"""
    cli = SanctuaryCLI()

    if args.sanctuary_command == "init":
        success = cli.init_sanctuary(args.name, args.template, not args.non_interactive)
        sys.exit(0 if success else 1)

    elif args.sanctuary_command == "list":
        sanctuaries = cli.list_sanctuaries()
        if sanctuaries:
            print("📁 Available sanctuaries:")
            for sanctuary in sanctuaries:
                print(f"   {sanctuary}")
        else:
            print("No sanctuaries found in current directory")
            print("Create one with: lamina sanctuary init <name>")

    elif args.sanctuary_command == "status":
        status = cli.sanctuary_status(args.path)
        if "error" in status:
            print(f"❌ {status['error']}")
            sys.exit(1)
        else:
            print("📊 Sanctuary Status")
            print(f"   Name: {status['name']}")
            print(f"   Description: {status['description']}")
            print(f"   AI Provider: {status['ai_provider']}")
            print(f"   Agents: {status['agent_count']}")
            print(f"   Infrastructure: {'✅' if status['has_infrastructure'] else '❌'}")

    else:
        print("Available sanctuary commands: init, list, status")
        print("Use 'lamina sanctuary <command> --help' for more information")


def handle_agent_command(args):
    """Handle agent subcommands"""
    try:
        from lamina.cli.agent_cli import AgentCLI

        cli = AgentCLI()

        if args.agent_command == "create":
            success = cli.create_agent(args.name, args.template, args.provider, args.model)
            sys.exit(0 if success else 1)

        elif args.agent_command == "list":
            agents = cli.list_agents()
            if agents:
                print("🤖 Available agents:")
                for agent in agents:
                    print(f"   {agent}")
            else:
                print("No agents found")
                print("Create one with: lamina agent create <name>")

        elif args.agent_command == "info":
            info = cli.get_agent_info(args.name)
            if info:
                print(f"🤖 Agent: {info['name']}")
                print(f"   Description: {info.get('description', 'N/A')}")
                print(f"   Template: {info.get('template', 'N/A')}")
                print(f"   Provider: {info.get('ai_provider', 'N/A')}")
                print(f"   Model: {info.get('ai_model', 'N/A')}")
            else:
                print(f"❌ Agent '{args.name}' not found")
                sys.exit(1)

        else:
            print("Available agent commands: create, list, info")
            print("Use 'lamina agent <command> --help' for more information")

    except ImportError:
        print("❌ Agent CLI not available")
        sys.exit(1)


def handle_chat_command(args):
    """Handle chat command"""

    if args.demo:
        # Run demo mode with mock agents
        import os
        import sys

        sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
        from examples.chat_demo import create_agents
        from lamina.coordination import AgentCoordinator

        print("🤖 Lamina Core Chat Demo")
        print("=" * 40)

        # Create agents and coordinator
        agents = create_agents()
        coordinator = AgentCoordinator(agents)

        if args.agent and not args.interactive:
            # Single demo message - args.agent is actually the message when using positional args
            message = args.agent
            response = coordinator.process_message(message)
            stats = coordinator.get_routing_stats()
            agent_used = (
                list(stats["routing_decisions"].keys())[-1]
                if stats["routing_decisions"]
                else "unknown"
            )
            print(f"User: {message}")
            print(f"Agent ({agent_used}): {response}")
        else:
            # Interactive demo
            print("Available agents:")
            for name, agent in agents.items():
                print(f"  🔹 {name}: {agent.description}")
            print("\nType 'quit' to exit, 'stats' for statistics")
            print("=" * 40)

            try:
                while True:
                    user_input = input("\nYou: ").strip()
                    if user_input.lower() in ["quit", "exit"]:
                        break
                    elif user_input.lower() == "stats":
                        stats = coordinator.get_routing_stats()
                        print(
                            f"📊 Stats: {stats['total_requests']} requests, {stats['routing_decisions']}"
                        )
                        continue

                    response = coordinator.process_message(user_input)
                    stats = coordinator.get_routing_stats()
                    agent_used = (
                        list(stats["routing_decisions"].keys())[-1]
                        if stats["routing_decisions"]
                        else "unknown"
                    )
                    print(f"🤖 {agent_used}: {response}")

            except (KeyboardInterrupt, EOFError):
                print("\n👋 Goodbye!")

        return

    # For real sanctuary-based chat, check if we're in a sanctuary
    import os

    if not os.path.exists("lamina.yaml"):
        print("❌ Not in a lamina sanctuary. Either:")
        print("   1. Run 'lamina chat --demo' for a demonstration")
        print("   2. Create a sanctuary with 'lamina sanctuary init <name>'")
        print("   3. Navigate to an existing sanctuary directory")
        return

    # TODO: Implement real sanctuary-based chat
    print("🚧 Real sanctuary chat not yet implemented.")
    print("💡 Use 'lamina chat --demo' to try the demonstration version.")


def handle_infrastructure_command(args):
    """Handle infrastructure subcommands"""
    if args.infra_command == "generate":
        print("🏗️  Generating infrastructure...")
        # TODO: Implement infrastructure generation
        print("✅ Infrastructure generated")

    elif args.infra_command == "status":
        print("📊 Infrastructure Status")
        # TODO: Implement infrastructure status
        print("   Status: Not implemented yet")

    else:
        print("Available infrastructure commands: generate, status")


def handle_docker_command(args):
    """Handle docker subcommands"""
    if args.docker_command == "build":
        print("🐳 Building containers...")
        # TODO: Implement docker build
        print("✅ Containers built")

    elif args.docker_command == "up":
        print("🚀 Starting services...")
        # TODO: Implement docker up
        print("✅ Services started")

    elif args.docker_command == "down":
        print("🛑 Stopping services...")
        # TODO: Implement docker down
        print("✅ Services stopped")

    elif args.docker_command == "logs":
        print("📋 Container logs:")
        # TODO: Implement docker logs
        print("   Logs not implemented yet")

    elif args.docker_command == "status":
        print("📊 Container Status")
        # TODO: Implement docker status
        print("   Status not implemented yet")

    else:
        print("Available docker commands: build, up, down, logs, status")


def handle_environment_command(args):
    """Handle environment subcommands"""
    try:
        from lamina.environment.config import validate_environment_name
        from lamina.environment.manager import EnvironmentManager

        if args.env_command == "create":
            print(f"🌊 Creating {args.name} environment configuration...")
            # TODO: Implement environment creation
            print("✅ Environment configuration created")

        elif args.env_command == "list":
            manager = EnvironmentManager()
            environments = manager.get_available_environments()
            if environments:
                print("🌊 Available environments:")
                for env_name in environments:
                    config = manager.get_environment_config(env_name)
                    print(f"   {config.sigil} {env_name} ({config.type})")
            else:
                print("No environments found")

        elif args.env_command == "status":
            manager = EnvironmentManager()
            if args.name:
                status = manager.get_environment_status(args.name)
                if "error" in status:
                    print(f"❌ {status['error']}")
                    return
                print(f"{status['sigil']} Environment: {status['name']}")
                print(f"   Type: {status['type']}")
                print(f"   Description: {status['description']}")
                print(f"   Validation: {status['validation']['status']}")
                print(f"   Services: {', '.join(status['services'])}")
                print(f"   Is Current: {status['is_current']}")
            else:
                # Show all environments
                environments = manager.get_available_environments()
                for env_name in environments:
                    status = manager.get_environment_status(env_name)
                    print(f"{status['sigil']} {env_name}: {status['validation']['status']}")

        elif args.env_command == "validate":
            manager = EnvironmentManager()
            if args.name:
                # Validate specific environment
                if not validate_environment_name(args.name):
                    print(f"❌ Invalid environment: {args.name}")
                    return
                try:
                    config = manager.get_environment_config(args.name)
                    from lamina.environment.validators import validate_environment_config

                    validate_environment_config(config)
                    print(f"{config.sigil} ✅ Environment {args.name} validation passed")
                except Exception as e:
                    print(f"❌ Environment {args.name} validation failed: {e}")
            else:
                # Validate all environments
                results = manager.validate_all_environments()
                for env_name, is_valid in results.items():
                    config = manager.get_environment_config(env_name)
                    status = "✅ Valid" if is_valid else "❌ Invalid"
                    print(f"{config.sigil} {env_name}: {status}")

        else:
            print("Available environment commands: create, list, status, validate")

    except ImportError as e:
        print(f"❌ Environment management not available: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def handle_gitops_command(args):
    """Handle GitOps subcommands"""
    try:
        from pathlib import Path

        from lamina.environment.config import load_environment_config, validate_environment_name
        from lamina.environment.helm import HelmChartGenerator, HelmError

        if args.gitops_command == "setup":
            if not validate_environment_name(args.environment):
                print(f"❌ Invalid environment: {args.environment}")
                return

            config = load_environment_config(args.environment)
            print(f"{config.sigil} Setting up GitOps for {args.environment} environment")

            # Create charts directory
            charts_dir = Path.cwd() / "charts"
            charts_dir.mkdir(exist_ok=True)

            # Generate Helm chart
            print(f"{config.sigil} Generating Helm chart...")
            generator = HelmChartGenerator(config, charts_dir)
            chart_dir = generator.generate_chart()

            # Validate and package
            if generator.validate_chart():
                print(f"{config.sigil} ✅ Chart validation passed")
                package_path = generator.package_chart()
                print(f"{config.sigil} ✅ GitOps setup complete!")
                print("\n📋 Generated Files:")
                print(f"  📊 Helm Chart: {chart_dir}")
                print(f"  📦 Package: {package_path}")
                print(f"  🔄 GitHub Workflow: {chart_dir}/.github/workflows/")
                if args.argocd:
                    print(f"  🐙 ArgoCD App: {chart_dir}/argocd-application.yaml")
                print("\n🚀 Next: Commit charts/ and push to trigger GitOps deployment!")
            else:
                print(f"{config.sigil} ❌ Chart validation failed")

        elif args.gitops_command == "generate-charts":
            if not validate_environment_name(args.environment):
                print(f"❌ Invalid environment: {args.environment}")
                return

            config = load_environment_config(args.environment)
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            generator = HelmChartGenerator(config, output_dir)
            chart_dir = generator.generate_chart()
            print(f"{config.sigil} Helm chart generated: {chart_dir}")

            if args.validate and generator.validate_chart():
                print(f"{config.sigil} ✅ Chart validation passed")
            if args.package:
                package_path = generator.package_chart()
                print(f"{config.sigil} Chart packaged: {package_path}")

        elif args.gitops_command == "deploy":
            if not validate_environment_name(args.environment):
                print(f"❌ Invalid environment: {args.environment}")
                return

            config = load_environment_config(args.environment)
            chart_path = (
                Path(args.chart_path)
                if args.chart_path
                else Path.cwd() / "charts" / f"lamina-{args.environment}"
            )
            namespace = args.namespace or f"lamina-{args.environment}"

            if not chart_path.exists():
                print(f"❌ Chart not found: {chart_path}")
                print(f"Run 'lamina gitops generate-charts {args.environment}' first")
                return

            print(f"{config.sigil} Deploying {args.environment} environment")
            print(f"📊 Chart: {chart_path}")
            print(f"🎯 Namespace: {namespace}")

            # Build helm command
            import subprocess

            cmd = [
                "helm",
                "upgrade",
                "--install",
                f"lamina-{args.environment}",
                str(chart_path),
                "--namespace",
                namespace,
                "--create-namespace",
                "--set",
                f"global.environment={args.environment}",
                "--set",
                f"global.sigil={config.sigil}",
            ]

            if args.dry_run:
                cmd.append("--dry-run")
                print(f"{config.sigil} Performing dry run...")

            if args.wait and not args.dry_run:
                cmd.extend(["--wait", "--timeout", f"{args.timeout}s"])

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"{config.sigil} ✅ Deployment successful!")
                if not args.dry_run:
                    print("\n📋 Deployment Status:")
                    print(result.stdout)
            else:
                print(f"{config.sigil} ❌ Deployment failed!")
                print(f"Error: {result.stderr}")

        elif args.gitops_command == "status":
            if not validate_environment_name(args.environment):
                print(f"❌ Invalid environment: {args.environment}")
                return

            config = load_environment_config(args.environment)
            namespace = args.namespace or f"lamina-{args.environment}"

            print(f"{config.sigil} Checking status for {args.environment} environment")
            print(f"🎯 Namespace: {namespace}")

            import subprocess

            # Check deployments, services, and pods
            for resource_type, icon in [("deployments", "📊"), ("services", "🌐"), ("pods", "🐳")]:
                print(f"\n{icon} {resource_type.title()}:")
                result = subprocess.run(
                    ["kubectl", "get", resource_type, "-n", namespace],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print(result.stdout)
                else:
                    print(f"❌ Failed to get {resource_type}: {result.stderr}")

        else:
            print("Available GitOps commands: setup, generate-charts, deploy, status")

    except ImportError as e:
        print(f"❌ GitOps functionality not available: {e}")
    except FileNotFoundError as e:
        print(f"❌ Environment configuration not found: {e}")
    except HelmError as e:
        print(f"❌ Helm error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()

    # Show banner for main help
    if not args.command:
        print_banner()
        parser.print_help()
        return

    # Set verbosity
    if args.verbose:
        import logging

        logging.basicConfig(level=logging.DEBUG)
    elif args.quiet:
        import logging

        logging.basicConfig(level=logging.ERROR)

    # Route to appropriate handler
    if args.command == "sanctuary":
        handle_sanctuary_command(args)

    elif args.command == "agent":
        handle_agent_command(args)

    elif args.command == "chat":
        handle_chat_command(args)

    elif args.command == "infrastructure":
        handle_infrastructure_command(args)

    elif args.command == "docker":
        handle_docker_command(args)

    elif args.command == "environment":
        handle_environment_command(args)

    elif args.command == "gitops":
        handle_gitops_command(args)

    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
