# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

# /lamina/api/unified_server.py

import argparse
import json
import os
import ssl

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi import Path as FastAPIPath
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from lamina.agent_config import load_agent_config
from lamina.chat import ChatSession
from lamina.infrastructure_config import get_infrastructure_config
from lamina.logging_config import LogContext, get_logger
from lamina.system_config import get_api_config, get_system_config

# Set up unified logging
logger = get_logger(__name__)

app = FastAPI(title="Lamina OS Unified Agent API", version="1.0.0")

# Global state for agent sessions and configurations
agent_sessions: dict[str, ChatSession] = {}
loaded_agents: dict[str, dict] = {}
DEFAULT_AGENT = None  # Will be set from command line args or system config


class ChatRequest(BaseModel):
    agent: str | None = None  # For backward compatibility with single-agent API
    message: str
    stream: bool = True


class AgentInteractionRequest(BaseModel):
    target_agent: str
    message: str
    context: str | None = None


@app.get("/health")
async def health_check():
    """Health check endpoint showing status of all loaded agents."""
    logger.info("Health check requested")

    if len(loaded_agents) == 1:
        # Single-agent mode compatibility
        agent_name = list(loaded_agents.keys())[0] if loaded_agents else DEFAULT_AGENT
        return {"status": "healthy", "agent": agent_name, "mode": "single-agent"}
    else:
        # Multi-agent mode
        return {
            "status": "healthy",
            "loaded_agents": list(loaded_agents.keys()),
            "active_sessions": list(agent_sessions.keys()),
            "mode": "multi-agent",
        }


@app.get("/agents")
async def list_agents():
    """List all available agents and their status."""
    system_config = get_system_config()

    # Get all agents from the registry
    agent_registry = system_config.agent_registry

    agents_info = {}
    for agent_name, agent_info in agent_registry.items():
        if agent_info.get("enabled", False):
            agents_info[agent_name] = {
                "enabled": agent_info.get("enabled", False),
                "auto_start": agent_info.get("auto_start", False),
                "priority": agent_info.get("priority", 0),
                "description": agent_info.get("description", ""),
                "loaded": agent_name in loaded_agents,
                "active_session": agent_name in agent_sessions,
            }

    return {"agents": agents_info}


@app.post("/chat")
async def chat_legacy(request: ChatRequest):
    """
    Legacy single-agent chat endpoint for backward compatibility.
    Routes to the appropriate agent based on request.agent or DEFAULT_AGENT.
    """
    # Get default agent from system config if not specified
    system_config = get_system_config()
    agent_name = request.agent or DEFAULT_AGENT or system_config.default_agent

    if not agent_name:
        logger.error("No agent specified in request and no default agent configured")
        raise HTTPException(
            status_code=400,
            detail="No agent specified in request and no default agent configured",
        )

    # Validate agent exists and is enabled
    if agent_name not in loaded_agents:
        # Try to load the agent
        try:
            await load_agent(agent_name)
        except Exception as e:
            logger.error(f"Failed to load agent {agent_name}: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_name}' not found or failed to load: {str(e)}",
            )

    # Use the unified chat logic
    return await _chat_with_agent(agent_name, request)


@app.post("/{agent_name}/chat")
async def chat_with_agent(
    agent_name: str = FastAPIPath(..., description="Name of the agent to chat with"),
    request: ChatRequest = None,
):
    """Chat with a specific agent using path-based routing."""

    # Validate agent exists and is enabled
    if agent_name not in loaded_agents:
        # Try to load the agent
        try:
            await load_agent(agent_name)
        except Exception as e:
            logger.error(f"Failed to load agent {agent_name}: {e}")
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_name}' not found or failed to load: {str(e)}",
            )

    # Use the unified chat logic
    return await _chat_with_agent(agent_name, request)


async def _chat_with_agent(agent_name: str, request: ChatRequest):
    """Unified chat logic used by both legacy and path-based endpoints."""

    # Use structured logging with context
    with LogContext(logger, agent=agent_name, message_length=len(request.message)):
        logger.info(
            f"Received chat request for agent: {agent_name}",
            extra={"agent": agent_name, "stream": request.stream},
        )

        # Get or create session for this agent
        if agent_name not in agent_sessions:
            logger.debug(f"Creating new session for agent: {agent_name}")
            agent_sessions[agent_name] = ChatSession(agent_name)

        session = agent_sessions[agent_name]

        # Handle input processing (memory, etc.) before adding to messages
        memory_response = session.handle_input(request.message)
        if memory_response:
            # Return memory response immediately
            return {"response": memory_response, "agent": agent_name}

        if request.stream:

            async def generate_response():
                try:
                    full_response = ""
                    # Stream the response using the full conversation history
                    async for chunk in session.query_ollama(session.messages, stream=True):
                        if chunk:  # Only yield non-empty chunks
                            full_response += chunk
                            yield json.dumps({"response": chunk, "agent": agent_name}) + "\n"

                    logger.info(
                        "Streaming response completed",
                        extra={
                            "agent": agent_name,
                            "response_length": len(full_response),
                        },
                    )

                except Exception as e:
                    logger.error(
                        f"Error in streaming response: {e}",
                        extra={"agent": agent_name},
                        exc_info=True,
                    )
                    yield json.dumps({"error": str(e), "agent": agent_name}) + "\n"

            return StreamingResponse(generate_response(), media_type="application/x-ndjson")
        else:
            try:
                full_response = ""
                # Collect the complete response
                async for chunk in session.query_ollama(session.messages, stream=False):
                    if chunk:
                        full_response += chunk

                logger.info(
                    "Non-streaming response completed",
                    extra={"agent": agent_name, "response_length": len(full_response)},
                )
                return {"response": full_response, "agent": agent_name}

            except Exception as e:
                logger.error(
                    f"Error in non-streaming response: {e}",
                    extra={"agent": agent_name},
                    exc_info=True,
                )
                raise HTTPException(status_code=500, detail=str(e))


@app.post("/{agent_name}/interact")
async def agent_interaction(
    agent_name: str = FastAPIPath(..., description="Name of the source agent"),
    request: AgentInteractionRequest = None,
):
    """
    Central orchestrator for agent-to-agent interactions.
    This endpoint allows one agent to communicate with another through a controlled interface.
    Only available when multiple agents are loaded.
    """

    # Check if we're in multi-agent mode
    if len(loaded_agents) <= 1:
        raise HTTPException(
            status_code=400,
            detail="Agent interactions are only available in multi-agent mode",
        )

    # Validate both agents exist
    if agent_name not in loaded_agents:
        raise HTTPException(status_code=404, detail=f"Source agent '{agent_name}' not found")

    if request.target_agent not in loaded_agents:
        try:
            await load_agent(request.target_agent)
        except Exception as e:
            raise HTTPException(
                status_code=404,
                detail=f"Target agent '{request.target_agent}' not found: {str(e)}",
            )

    with LogContext(
        logger,
        source_agent=agent_name,
        target_agent=request.target_agent,
        interaction_type="agent_to_agent",
    ):

        logger.info(
            f"Agent interaction: {agent_name} -> {request.target_agent}",
            extra={
                "source_agent": agent_name,
                "target_agent": request.target_agent,
                "message_length": len(request.message),
            },
        )

        # Get or create session for target agent
        if request.target_agent not in agent_sessions:
            agent_sessions[request.target_agent] = ChatSession(request.target_agent)

        target_session = agent_sessions[request.target_agent]

        # Prefix the message with context about the source agent
        contextual_message = f"[From {agent_name}]: {request.message}"
        if request.context:
            contextual_message = (
                f"[From {agent_name}, Context: {request.context}]: {request.message}"
            )

        # Handle the interaction through the target agent
        memory_response = target_session.handle_input(contextual_message)
        if memory_response:
            return {
                "response": memory_response,
                "source_agent": agent_name,
                "target_agent": request.target_agent,
                "interaction_type": "memory",
            }

        # Generate response from target agent
        try:
            full_response = ""
            async for chunk in target_session.query_ollama(target_session.messages, stream=False):
                if chunk:
                    full_response += chunk

            logger.info(
                "Agent interaction completed",
                extra={
                    "source_agent": agent_name,
                    "target_agent": request.target_agent,
                    "response_length": len(full_response),
                },
            )

            return {
                "response": full_response,
                "source_agent": agent_name,
                "target_agent": request.target_agent,
                "interaction_type": "chat",
            }

        except Exception as e:
            logger.error(
                f"Error in agent interaction: {e}",
                extra={
                    "source_agent": agent_name,
                    "target_agent": request.target_agent,
                },
                exc_info=True,
            )
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/{agent_name}/memory")
async def get_agent_memory(
    agent_name: str = FastAPIPath(..., description="Name of the agent"), limit: int = 10
):
    """Get recent memory/conversation history for an agent."""
    if agent_name not in agent_sessions:
        raise HTTPException(
            status_code=404, detail=f"No active session found for agent '{agent_name}'"
        )

    session = agent_sessions[agent_name]
    recent_messages = session.messages[-limit:] if session.messages else []

    return {
        "agent": agent_name,
        "memory": [{"role": msg.role, "content": msg.content} for msg in recent_messages],
        "total_messages": len(session.messages),
    }


async def load_agent(agent_name: str) -> dict:
    """Load an agent configuration and validate it's available."""
    try:
        # Load agent configuration
        agent_config = load_agent_config(agent_name)

        # Validate agent is enabled in system config
        system_config = get_system_config()
        agent_registry = system_config.agent_registry

        if agent_name not in agent_registry:
            raise ValueError(f"Agent '{agent_name}' not found in system registry")

        agent_info = agent_registry[agent_name]
        if not agent_info.get("enabled", False):
            raise ValueError(f"Agent '{agent_name}' is not enabled")

        # Store the loaded configuration
        loaded_agents[agent_name] = {
            "config": agent_config,
            "registry_info": agent_info,
        }

        logger.info(f"Successfully loaded agent: {agent_name}")
        return loaded_agents[agent_name]

    except Exception as e:
        logger.error(f"Failed to load agent {agent_name}: {e}")
        raise


async def load_enabled_agents(specific_agent: str = None):
    """Load enabled agents from the system configuration."""
    system_config = get_system_config()
    agent_registry = system_config.agent_registry

    if specific_agent:
        # Single-agent mode: load only the specified agent
        if specific_agent in agent_registry and agent_registry[specific_agent].get(
            "enabled", False
        ):
            try:
                await load_agent(specific_agent)
                logger.info(f"Loaded single agent: {specific_agent}")
            except Exception as e:
                logger.error(f"Failed to load specified agent {specific_agent}: {e}")
                raise
        else:
            raise ValueError(f"Agent '{specific_agent}' not found or not enabled")
    else:
        # Multi-agent mode: load all enabled agents
        loaded_count = 0
        for agent_name, agent_info in agent_registry.items():
            if agent_info.get("enabled", False):
                try:
                    await load_agent(agent_name)
                    loaded_count += 1
                except Exception as e:
                    logger.warning(f"Failed to load enabled agent {agent_name}: {e}")

        if loaded_count == 0:
            raise ValueError("No enabled agents found in system configuration")

        logger.info(f"Loaded {loaded_count} agents successfully")


def get_ssl_context() -> ssl.SSLContext:
    """Create SSL context for mTLS using configuration."""
    infra_config = get_infrastructure_config()
    ssl_config = infra_config.get_ssl_config()

    # Create SSL context with protocol configuration
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    # Use the default agent or first loaded agent for SSL certificates
    # Don't use AGENT_NAME if it's "multi-agent" (server mode, not an agent)
    agent_name_env = os.getenv("AGENT_NAME", "clara")
    if agent_name_env == "multi-agent":
        agent_name_env = "clara"  # Default to clara for multi-agent mode

    default_agent = DEFAULT_AGENT or agent_name_env

    # Load server's certificate and private key using config paths
    ssl_context.load_cert_chain(
        certfile=infra_config.get_cert_path(default_agent, "cert_file"),
        keyfile=infra_config.get_cert_path(default_agent, "key_file"),
    )

    # Load CA certificate for client verification
    ssl_context.load_verify_locations(cafile=infra_config.get_cert_path("ca", "cert_file"))

    # Configure client verification based on config
    if ssl_config.get("verify_client", True):
        ssl_context.verify_mode = ssl.CERT_REQUIRED
    else:
        ssl_context.verify_mode = ssl.CERT_NONE

    # Configure secure settings
    min_tls_version = ssl_config.get("min_tls_version", "TLSv1_2")
    if hasattr(ssl.TLSVersion, min_tls_version):
        ssl_context.minimum_version = getattr(ssl.TLSVersion, min_tls_version)
    else:
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

    return ssl_context


async def startup_event():
    """Load agents on startup based on configuration."""
    logger.info("Starting unified agent server...")

    if DEFAULT_AGENT:
        # Single-agent mode
        logger.info(f"Starting in single-agent mode with agent: {DEFAULT_AGENT}")
        await load_enabled_agents(specific_agent=DEFAULT_AGENT)
    else:
        # Multi-agent mode
        logger.info("Starting in multi-agent mode")
        await load_enabled_agents()


# Register startup event
app.add_event_handler("startup", startup_event)


def main():
    global DEFAULT_AGENT

    # Load system and infrastructure configuration
    get_system_config()
    api_config = get_api_config()
    infra_config = get_infrastructure_config()
    ssl_config = infra_config.get_ssl_config()

    parser = argparse.ArgumentParser(description="Run the Lamina unified agent server")
    parser.add_argument(
        "--port",
        type=int,
        default=api_config.get("port", 8001),
        help=f"Port to run the server on (default: {api_config.get('port', 8001)})",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=api_config.get("host", "localhost"),
        help=f"Host to bind the server to (default: {api_config.get('host', 'localhost')})",
    )
    parser.add_argument(
        "--agent",
        type=str,
        help="Run in single-agent mode with specified agent (omit for multi-agent mode)",
    )
    args = parser.parse_args()

    DEFAULT_AGENT = args.agent

    # Validate SSL configuration
    try:
        get_ssl_context()
        logger.info("SSL context validated successfully")
    except Exception as e:
        logger.error(f"Failed to create SSL context: {e}")
        return

    mode = "single-agent" if DEFAULT_AGENT else "multi-agent"
    logger.info(f"Starting unified server in {mode} mode on {args.host}:{args.port}")
    if DEFAULT_AGENT:
        logger.info(f"Single agent: {DEFAULT_AGENT}")

    # Configure SSL certificate requirements based on config
    ssl_cert_reqs = ssl.CERT_REQUIRED if ssl_config.get("verify_client", True) else ssl.CERT_NONE

    # Use the specified agent or default for SSL certificates
    # Don't use AGENT_NAME if it's "multi-agent" (server mode, not an agent)
    agent_name_env = os.getenv("AGENT_NAME", "clara")
    if agent_name_env == "multi-agent":
        agent_name_env = "clara"  # Default to clara for multi-agent mode

    cert_agent = DEFAULT_AGENT or agent_name_env

    uvicorn.run(
        "lamina.api.unified_server:app",
        host=args.host,
        port=args.port,
        ssl_keyfile=infra_config.get_cert_path(cert_agent, "key_file"),
        ssl_certfile=infra_config.get_cert_path(cert_agent, "cert_file"),
        ssl_ca_certs=infra_config.get_cert_path("ca", "cert_file"),
        ssl_cert_reqs=ssl_cert_reqs,
    )


if __name__ == "__main__":
    main()
