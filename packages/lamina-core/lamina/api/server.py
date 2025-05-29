# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

# /lamina/api/server.py

import argparse
import json
import os
import ssl

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from lamina.agent_config import load_agent_config
from lamina.chat import ChatSession
from lamina.infrastructure_config import get_infrastructure_config
from lamina.logging_config import LogContext, get_logger
from lamina.system_config import get_api_config, get_system_config

# Set up unified logging
logger = get_logger(__name__)

app = FastAPI()
sessions = {}
DEFAULT_AGENT = None  # Will be set from command line args or system config


@app.get("/health")
async def health_check():
    logger.info("Health check requested", extra={"agent": DEFAULT_AGENT})
    return {"status": "healthy", "agent": DEFAULT_AGENT}


class ChatRequest(BaseModel):
    agent: str | None = None
    message: str
    stream: bool = True  # Default to streaming for backward compatibility


@app.post("/chat")
async def chat(request: ChatRequest):
    # Get default agent from system config if not specified
    system_config = get_system_config()
    agent_name = request.agent or DEFAULT_AGENT or system_config.default_agent

    if not agent_name:
        logger.error("No agent specified in request and no default agent configured")
        raise HTTPException(
            status_code=400,
            detail="No agent specified in request and no default agent configured",
        )

    # Use structured logging with context
    with LogContext(logger, agent=agent_name, message_length=len(request.message)):
        logger.info(
            "Received chat request",
            extra={"agent": agent_name, "stream": request.stream},
        )

        if agent_name not in sessions:
            logger.debug(f"Creating new session for agent: {agent_name}")
            sessions[agent_name] = ChatSession(agent_name)

        session = sessions[agent_name]

        # Handle input processing (memory, etc.) before adding to messages
        memory_response = session.handle_input(request.message)
        if memory_response:
            # Return memory response immediately
            return {"response": memory_response}

        if request.stream:

            async def generate_response():
                try:
                    full_response = ""
                    # Stream the response using the full conversation history
                    async for chunk in session.query_ollama(session.messages, stream=True):
                        if chunk:  # Only yield non-empty chunks
                            full_response += chunk
                            yield json.dumps({"response": chunk}) + "\n"

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
                    yield json.dumps({"error": str(e)}) + "\n"

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
                return {"response": full_response}

            except Exception as e:
                logger.error(
                    f"Error in non-streaming response: {e}",
                    extra={"agent": agent_name},
                    exc_info=True,
                )
                raise HTTPException(status_code=500, detail=str(e))


def get_ssl_context() -> ssl.SSLContext:
    """Create SSL context for mTLS using configuration."""
    infra_config = get_infrastructure_config()
    ssl_config = infra_config.get_ssl_config()

    # Create SSL context with protocol configuration
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)

    # Load server's certificate and private key using config paths
    ssl_context.load_cert_chain(
        certfile=infra_config.get_cert_path(os.getenv("AGENT_NAME", "example"), "cert_file"),
        keyfile=infra_config.get_cert_path(os.getenv("AGENT_NAME", "example"), "key_file"),
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


def main():
    global DEFAULT_AGENT

    # Load system and infrastructure configuration
    system_config = get_system_config()
    api_config = get_api_config()
    infra_config = get_infrastructure_config()
    ssl_config = infra_config.get_ssl_config()

    parser = argparse.ArgumentParser(description="Run the Lamina chat server")
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
        default=system_config.default_agent,
        help=f"Name of the agent to use (default: {system_config.default_agent})",
    )
    args = parser.parse_args()
    DEFAULT_AGENT = args.agent

    # Validate that the agent exists
    try:
        load_agent_config(DEFAULT_AGENT)
        logger.info(f"Loaded configuration for agent: {DEFAULT_AGENT}")
    except Exception as e:
        logger.error(f"Failed to load agent configuration for {DEFAULT_AGENT}: {e}")
        return

    get_ssl_context()
    logger.info(f"Starting server on {args.host}:{args.port} with agent {DEFAULT_AGENT}")

    # Configure SSL certificate requirements based on config
    ssl_cert_reqs = ssl.CERT_REQUIRED if ssl_config.get("verify_client", True) else ssl.CERT_NONE

    uvicorn.run(
        "lamina.api.server:app",
        host=args.host,
        port=args.port,
        ssl_keyfile=infra_config.get_cert_path(os.getenv("AGENT_NAME", "example"), "key_file"),
        ssl_certfile=infra_config.get_cert_path(os.getenv("AGENT_NAME", "example"), "cert_file"),
        ssl_ca_certs=infra_config.get_cert_path("ca", "cert_file"),
        ssl_cert_reqs=ssl_cert_reqs,
    )


if __name__ == "__main__":
    main()
