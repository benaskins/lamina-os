"""
Main CLI Entry Point

Unified command-line interface for all Lamina Core operations including
sanctuary management, agent creation, and system operations.
"""

import argparse
import sys
from typing import List, Optional

from lamina.cli.sanctuary_cli import SanctuaryCLI
from lamina.cli.agent_cli import AgentCLI
from lamina.cli.unified_cli import main as unified_cli_main


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
"""
    )
    
    # Global options
    parser.add_argument("--version", action="version", version="lamina-core 0.1.0")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Sanctuary management
    sanctuary_parser = subparsers.add_parser(
        "sanctuary", 
        help="Sanctuary management and scaffolding"
    )
    sanctuary_subparsers = sanctuary_parser.add_subparsers(dest="sanctuary_command")
    
    # sanctuary init
    init_parser = sanctuary_subparsers.add_parser("init", help="Initialize new sanctuary")
    init_parser.add_argument("name", help="Sanctuary name")
    init_parser.add_argument("--template", choices=["basic", "advanced", "custom"], 
                           default="basic", help="Sanctuary template")
    init_parser.add_argument("--non-interactive", action="store_true", 
                           help="Use default configuration")
    
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
    create_parser.add_argument("--template", choices=["conversational", "analytical", "security", "reasoning"],
                             default="conversational", help="Agent template")
    create_parser.add_argument("--provider", choices=["ollama", "huggingface"],
                             default="ollama", help="AI provider")
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
    
    return parser


def handle_sanctuary_command(args):
    """Handle sanctuary subcommands"""
    cli = SanctuaryCLI()
    
    if args.sanctuary_command == "init":
        success = cli.init_sanctuary(
            args.name, 
            args.template, 
            not args.non_interactive
        )
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
            print(f"📊 Sanctuary Status")
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
            success = cli.create_agent(
                args.name,
                args.template,
                args.provider,
                args.model
            )
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
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
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
            agent_used = list(stats['routing_decisions'].keys())[-1] if stats['routing_decisions'] else 'unknown'
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
                    if user_input.lower() in ['quit', 'exit']:
                        break
                    elif user_input.lower() == 'stats':
                        stats = coordinator.get_routing_stats()
                        print(f"📊 Stats: {stats['total_requests']} requests, {stats['routing_decisions']}")
                        continue
                    
                    response = coordinator.process_message(user_input)
                    stats = coordinator.get_routing_stats()
                    agent_used = list(stats['routing_decisions'].keys())[-1] if stats['routing_decisions'] else 'unknown'
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
    
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()