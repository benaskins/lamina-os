# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

#!/usr/bin/env python3
"""
Unified CLI for Lamina OS

This CLI automatically detects whether the server is running in single-agent or multi-agent mode
and provides the appropriate interface.
"""

import argparse
import json
import sys

import requests
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from lamina.infrastructure_config import get_infrastructure_config
from lamina.logging_config import get_logger

# Disable SSL warnings for localhost development
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = get_logger(__name__)


class UnifiedCLI:
    def __init__(self, base_url: str, cert_path: tuple):
        self.base_url = base_url
        self.cert_path = cert_path
        self.session = self._create_session()
        self.server_mode = None
        self.available_agents = {}

        # Detect server mode on initialization
        self._detect_server_mode()

    def _create_session(self):
        """Create a requests session with retry strategy and SSL configuration."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def _detect_server_mode(self):
        """Detect if the server is running in single-agent or multi-agent mode."""
        try:
            # Check health endpoint to determine mode
            response = self.session.get(
                f"{self.base_url}/health", cert=self.cert_path, verify=False
            )
            response.raise_for_status()
            health_data = response.json()

            self.server_mode = health_data.get("mode", "unknown")

            # Get available agents
            agents_response = self.session.get(
                f"{self.base_url}/agents", cert=self.cert_path, verify=False
            )
            if agents_response.status_code == 200:
                agents_data = agents_response.json()
                self.available_agents = agents_data.get("agents", {})
            elif self.server_mode == "single-agent":
                # For single-agent mode, create a mock agent entry
                agent_name = health_data.get("agent", "unknown")
                self.available_agents = {
                    agent_name: {
                        "enabled": True,
                        "loaded": True,
                        "description": f"Single agent: {agent_name}",
                    }
                }

            logger.info(f"Detected server mode: {self.server_mode}")

        except Exception as e:
            logger.warning(f"Failed to detect server mode: {e}")
            self.server_mode = "unknown"
            self.available_agents = {}

    def list_agents(self) -> dict:
        """List all available agents."""
        return {"agents": self.available_agents}

    def chat_with_agent(self, agent_name: str, message: str, stream: bool = False) -> str:
        """Send a message to a specific agent."""
        try:
            payload = {"message": message, "stream": stream}

            # Choose endpoint based on server mode
            if self.server_mode == "single-agent":
                # Use legacy endpoint with agent parameter
                payload["agent"] = agent_name
                endpoint = f"{self.base_url}/chat"
            else:
                # Use path-based routing
                endpoint = f"{self.base_url}/{agent_name}/chat"

            response = self.session.post(endpoint, json=payload, cert=self.cert_path, verify=False)
            response.raise_for_status()

            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode("utf-8"))
                            if "response" in data:
                                chunk = data["response"]
                                print(chunk, end="", flush=True)
                                full_response += chunk
                            elif "error" in data:
                                print(f"\nError: {data['error']}")
                                return ""
                        except json.JSONDecodeError:
                            continue
                print()  # New line after streaming
                return full_response
            else:
                data = response.json()
                return data.get("response", "")

        except Exception as e:
            logger.error(f"Failed to chat with {agent_name}: {e}")
            return f"Error: {e}"

    def agent_interaction(
        self,
        source_agent: str,
        target_agent: str,
        message: str,
        context: str | None = None,
    ) -> str:
        """Facilitate interaction between two agents (multi-agent mode only)."""
        if self.server_mode != "multi-agent":
            return "Error: Agent interactions are only available in multi-agent mode"

        try:
            payload = {"target_agent": target_agent, "message": message}
            if context:
                payload["context"] = context

            response = self.session.post(
                f"{self.base_url}/{source_agent}/interact",
                json=payload,
                cert=self.cert_path,
                verify=False,
            )
            response.raise_for_status()

            data = response.json()
            return data.get("response", "")

        except Exception as e:
            logger.error(f"Failed agent interaction {source_agent} -> {target_agent}: {e}")
            return f"Error: {e}"

    def get_agent_memory(self, agent_name: str, limit: int = 10) -> dict:
        """Get recent memory for an agent."""
        try:
            response = self.session.get(
                f"{self.base_url}/{agent_name}/memory?limit={limit}",
                cert=self.cert_path,
                verify=False,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get memory for {agent_name}: {e}")
            return {"memory": [], "total_messages": 0}


def interactive_mode(cli: UnifiedCLI):
    """Run the CLI in interactive mode."""
    mode_emoji = "🌟" if cli.server_mode == "multi-agent" else "🤖"
    print(f"{mode_emoji} Lamina OS Unified CLI ({cli.server_mode} mode)")
    print("=" * 60)

    # List available agents
    agents = cli.available_agents

    if not agents:
        print("❌ No agents available")
        return

    print("Available agents:")
    for agent_name, info in agents.items():
        status = "🟢" if info.get("loaded", False) else "🔴"
        symbol = {"clara": "🪶", "luna": "🔥", "phi": "🧠"}.get(agent_name, "🤖")
        print(f"  {status} {symbol} {agent_name}: {info.get('description', '')}")

    print("\nCommands:")
    print("  @agent_name message     - Chat with specific agent")
    if cli.server_mode == "multi-agent":
        print("  agent1 -> agent2: msg   - Agent-to-agent interaction")
    print("  /memory agent_name      - Show agent memory")
    print("  /agents                 - List agents")
    print("  /help                   - Show this help")
    print("  /quit or Ctrl+C         - Exit")
    print()

    current_agent = None

    # Auto-select agent in single-agent mode
    if cli.server_mode == "single-agent" and len(agents) == 1:
        current_agent = list(agents.keys())[0]
        symbol = {"clara": "🪶", "luna": "🔥", "phi": "🧠"}.get(current_agent, "🤖")
        print(f"🔄 Auto-selected {symbol} {current_agent} (single-agent mode)")
        print()

    while True:
        try:
            if current_agent:
                prompt = f"{current_agent} > "
            else:
                prompt = f"{cli.server_mode} > "

            line = input(prompt).strip()

            if not line:
                continue

            # Handle commands
            if line.startswith("/"):
                command = line[1:].lower()

                if command == "quit" or command == "exit":
                    break
                elif command == "help":
                    print("\nCommands:")
                    print("  @agent_name message     - Chat with specific agent")
                    if cli.server_mode == "multi-agent":
                        print("  agent1 -> agent2: msg   - Agent-to-agent interaction")
                    print("  /memory agent_name      - Show agent memory")
                    print("  /agents                 - List agents")
                    print("  /help                   - Show this help")
                    print("  /quit                   - Exit")
                elif command == "agents":
                    for agent_name, info in agents.items():
                        status = "🟢" if info.get("loaded", False) else "🔴"
                        symbol = {"clara": "🪶", "luna": "🔥", "phi": "🧠"}.get(agent_name, "🤖")
                        print(f"  {status} {symbol} {agent_name}: {info.get('description', '')}")
                elif command.startswith("memory "):
                    agent_name = command[7:].strip()
                    if agent_name in agents:
                        memory_info = cli.get_agent_memory(agent_name)
                        print(
                            f"\n{agent_name} memory ({memory_info.get('total_messages', 0)} total messages):"
                        )
                        for msg in memory_info.get("memory", []):
                            role_symbol = "👤" if msg["role"] == "user" else "🤖"
                            print(f"  {role_symbol} {msg['role']}: {msg['content'][:100]}...")
                    else:
                        print(f"❌ Agent '{agent_name}' not found")
                else:
                    print(f"❌ Unknown command: {command}")
                continue

            # Handle agent selection (@agent_name)
            if line.startswith("@"):
                parts = line[1:].split(" ", 1)
                if len(parts) == 2:
                    agent_name, message = parts
                    if agent_name in agents:
                        symbol = {"clara": "🪶", "luna": "🔥", "phi": "🧠"}.get(agent_name, "🤖")
                        print(f"{symbol} {agent_name}: ", end="")
                        response = cli.chat_with_agent(agent_name, message, stream=True)
                    else:
                        print(f"❌ Agent '{agent_name}' not found")
                elif len(parts) == 1:
                    # Switch to agent mode
                    agent_name = parts[0]
                    if agent_name in agents:
                        current_agent = agent_name
                        symbol = {"clara": "🪶", "luna": "🔥", "phi": "🧠"}.get(agent_name, "🤖")
                        print(f"🔄 Switched to {symbol} {agent_name}")
                    else:
                        print(f"❌ Agent '{agent_name}' not found")
                continue

            # Handle agent-to-agent interaction (multi-agent mode only)
            if cli.server_mode == "multi-agent" and " -> " in line and ":" in line:
                try:
                    interaction_part, message = line.split(":", 1)
                    source_agent, target_agent = interaction_part.split(" -> ")
                    source_agent = source_agent.strip()
                    target_agent = target_agent.strip()
                    message = message.strip()

                    if source_agent in agents and target_agent in agents:
                        source_symbol = {"clara": "🪶", "luna": "🔥", "phi": "🧠"}.get(
                            source_agent, "🤖"
                        )
                        target_symbol = {"clara": "🪶", "luna": "🔥", "phi": "🧠"}.get(
                            target_agent, "🤖"
                        )
                        print(f"{source_symbol} {source_agent} → {target_symbol} {target_agent}")
                        response = cli.agent_interaction(source_agent, target_agent, message)
                        print(f"{target_symbol} {target_agent}: {response}")
                    else:
                        print(f"❌ One or both agents not found: {source_agent}, {target_agent}")
                except ValueError:
                    print("❌ Invalid interaction format. Use: agent1 -> agent2: message")
                continue

            # Handle regular chat with current agent
            if current_agent:
                symbol = {"clara": "🪶", "luna": "🔥", "phi": "🧠"}.get(current_agent, "🤖")
                print(f"{symbol} {current_agent}: ", end="")
                response = cli.chat_with_agent(current_agent, line, stream=True)
            else:
                if cli.server_mode == "single-agent" and len(agents) == 1:
                    # Auto-chat with the single agent
                    agent_name = list(agents.keys())[0]
                    symbol = {"clara": "🪶", "luna": "🔥", "phi": "🧠"}.get(agent_name, "🤖")
                    print(f"{symbol} {agent_name}: ", end="")
                    response = cli.chat_with_agent(agent_name, line, stream=True)
                else:
                    print(
                        "❌ No agent selected. Use @agent_name to select an agent or @agent_name message to chat directly"
                    )

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except EOFError:
            print("\n👋 Goodbye!")
            break


def main():
    parser = argparse.ArgumentParser(description="Lamina OS Unified CLI")
    parser.add_argument("--agent", type=str, help="Start in single-agent mode with specified agent")
    parser.add_argument("--message", type=str, help="Send a single message (requires --agent)")
    parser.add_argument(
        "--interaction",
        type=str,
        help="Agent interaction in format 'source_agent->target_agent:message' (multi-agent mode only)",
    )
    parser.add_argument(
        "--list-agents", action="store_true", help="List all available agents and exit"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="API server host (default: localhost)",
    )
    parser.add_argument("--port", type=int, default=443, help="API server port (default: 443)")

    args = parser.parse_args()

    # Build API URL
    api_url = f"https://{args.host}:{args.port}"

    # Get certificate paths from configuration
    infra_config = get_infrastructure_config()
    cert_path = (
        infra_config.get_cert_path("clara", "cert_file"),  # Use Clara's cert for client auth
        infra_config.get_cert_path("clara", "key_file"),
    )

    # Create CLI instance
    cli = UnifiedCLI(api_url, cert_path)

    # Handle different modes
    if args.list_agents:
        agents_info = cli.list_agents()
        agents = agents_info.get("agents", {})
        print(f"Available agents ({cli.server_mode} mode):")
        for agent_name, info in agents.items():
            status = "🟢" if info.get("loaded", False) else "🔴"
            symbol = {"clara": "🪶", "luna": "🔥", "phi": "🧠"}.get(agent_name, "🤖")
            print(f"  {status} {symbol} {agent_name}: {info.get('description', '')}")
        return

    if args.interaction:
        # Handle agent interaction (multi-agent mode only)
        if cli.server_mode != "multi-agent":
            print("❌ Agent interactions are only available in multi-agent mode")
            sys.exit(1)

        try:
            interaction_part, message = args.interaction.split(":", 1)
            source_agent, target_agent = interaction_part.split("->")
            source_agent = source_agent.strip()
            target_agent = target_agent.strip()
            message = message.strip()

            response = cli.agent_interaction(source_agent, target_agent, message)
            print(f"{target_agent}: {response}")
        except ValueError:
            print("❌ Invalid interaction format. Use: source_agent->target_agent:message")
            sys.exit(1)
        return

    if args.agent and args.message:
        # Single message mode
        response = cli.chat_with_agent(args.agent, args.message, stream=False)
        print(f"{args.agent}: {response}")
        return

    if args.agent:
        # Single agent mode
        agents = cli.available_agents
        if args.agent not in agents:
            print(f"❌ Agent '{args.agent}' not found")
            sys.exit(1)

        symbol = {"clara": "🪶", "luna": "🔥", "phi": "🧠"}.get(args.agent, "🤖")
        print(f"{symbol} Chatting with {args.agent}")
        print("Type 'exit' or Ctrl+C to quit.\n")

        while True:
            try:
                message = input(f"{args.agent} > ")
                if message.lower() in ["exit", "quit"]:
                    break

                print(f"{symbol} {args.agent}: ", end="")
                response = cli.chat_with_agent(args.agent, message, stream=True)

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
        return

    # Default to interactive mode
    interactive_mode(cli)


if __name__ == "__main__":
    main()
