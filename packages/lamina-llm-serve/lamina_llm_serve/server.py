# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
LLM Server - HTTP server for managing and serving models

Provides REST API for model discovery, backend management,
and proxy endpoints for active model servers.
"""

import logging
import subprocess
import time
from pathlib import Path
from typing import Any

import requests
from flask import Flask, Response, jsonify, request

from lamina_llm_serve.backends import get_backend_for_model, list_available_backends
from lamina_llm_serve.model_manager import ModelManager

logger = logging.getLogger(__name__)


class LLMServer:
    """
    HTTP server for the Lamina LLM cache and serving layer.

    Provides endpoints for:
    - Model discovery and metadata
    - Backend status and management
    - Proxy to running model servers
    - Health checking and monitoring
    """

    def __init__(self, manifest_path: str = "models.yaml", models_dir: str = "models"):
        self.app = Flask(__name__)
        self.model_manager = ModelManager(manifest_path, models_dir)
        self.active_servers = (
            {}
        )  # model_name -> {'process': process, 'port': port, 'backend': backend}
        self.base_port = 8081  # Start port allocation from here

        self._setup_routes()

    def _setup_routes(self):
        """Set up Flask routes"""

        @self.app.route("/health", methods=["GET"])
        def health():
            """Health check endpoint"""
            stats = self.model_manager.get_model_stats()
            return jsonify(
                {
                    "status": "healthy",
                    "timestamp": time.time(),
                    "models": stats,
                    "active_servers": len(self.active_servers),
                }
            )

        @self.app.route("/models", methods=["GET"])
        def list_models():
            """List all available models"""
            models = {}
            for model_name in self.model_manager.list_models():
                model_info = self.model_manager.get_model_info(model_name)
                models[model_name] = {
                    **model_info,
                    "available": self.model_manager.is_model_available(model_name),
                    "active": model_name in self.active_servers,
                }

            return jsonify(
                {
                    "models": models,
                    "total": len(models),
                    "available": sum(1 for m in models.values() if m["available"]),
                    "active": len(self.active_servers),
                }
            )

        @self.app.route("/models/<model_name>", methods=["GET"])
        def get_model(model_name):
            """Get detailed information about a specific model"""
            model_info = self.model_manager.get_model_info(model_name)
            if not model_info:
                return jsonify({"error": "Model not found"}), 404

            result = {
                **model_info,
                "available": self.model_manager.is_model_available(model_name),
                "active": model_name in self.active_servers,
            }

            if model_name in self.active_servers:
                server_info = self.active_servers[model_name]
                result["server"] = {
                    "port": server_info["port"],
                    "backend": server_info["backend"].name,
                    "health_endpoint": server_info["backend"].get_health_endpoint(
                        server_info["port"]
                    ),
                    "chat_endpoint": server_info["backend"].get_chat_endpoint(server_info["port"]),
                }

            return jsonify(result)

        @self.app.route("/models/<model_name>/start", methods=["POST"])
        def start_model(model_name):
            """Start a server for the specified model"""
            try:
                result = self._start_model_server(model_name)
                return jsonify(result)
            except Exception as e:
                logger.error(f"Failed to start model {model_name}: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/models/<model_name>/stop", methods=["POST"])
        def stop_model(model_name):
            """Stop the server for the specified model"""
            try:
                result = self._stop_model_server(model_name)
                return jsonify(result)
            except Exception as e:
                logger.error(f"Failed to stop model {model_name}: {e}")
                return jsonify({"error": str(e)}), 500

        @self.app.route("/backends", methods=["GET"])
        def list_backends():
            """List all available backends"""
            backend_configs = self.model_manager.backends
            available = list_available_backends(backend_configs)

            return jsonify(
                {
                    "backends": backend_configs,
                    "available": available,
                    "total_configured": len(backend_configs),
                    "total_available": len(available),
                }
            )

        @self.app.route("/suggest", methods=["POST"])
        def suggest_model():
            """Suggest a model based on requirements"""
            requirements = request.get_json() or {}
            suggested = self.model_manager.suggest_model(requirements)

            if suggested:
                model_info = self.model_manager.get_model_info(suggested)
                return jsonify(
                    {
                        "suggested": suggested,
                        "model_info": model_info,
                        "available": self.model_manager.is_model_available(suggested),
                    }
                )
            else:
                return jsonify({"error": "No suitable model found"}), 404

        @self.app.route("/chat/<model_name>", methods=["POST"])
        def chat_proxy(model_name):
            """Proxy chat requests to active model servers"""
            if model_name not in self.active_servers:
                return jsonify({"error": "Model server not active"}), 404

            server_info = self.active_servers[model_name]
            chat_endpoint = server_info["backend"].get_chat_endpoint(server_info["port"])

            try:
                # Proxy the request
                response = requests.post(
                    chat_endpoint,
                    json=request.get_json(),
                    headers={"Content-Type": "application/json"},
                    timeout=30,
                )

                return Response(
                    response.content,
                    status=response.status_code,
                    headers={"Content-Type": "application/json"},
                )

            except Exception as e:
                logger.error(f"Error proxying to {model_name}: {e}")
                return jsonify({"error": "Model server error"}), 502

        @self.app.route("/v1/chat/completions", methods=["POST"])
        def chat_completions():
            """OpenAI-compatible chat completions endpoint"""
            try:
                request_data = request.get_json()
                if not request_data:
                    return jsonify({"error": "Invalid JSON request"}), 400

                # Extract required parameters
                model_name = request_data.get("model")
                messages = request_data.get("messages", [])
                stream = request_data.get("stream", False)

                if not model_name:
                    return jsonify({"error": "Missing required parameter: model"}), 400

                if not messages:
                    return jsonify({"error": "Missing required parameter: messages"}), 400

                # Validate model exists in registry
                model_info = self.model_manager.get_model_info(model_name)
                if not model_info:
                    available_models = list(self.model_manager.list_models())
                    return (
                        jsonify(
                            {
                                "error": f"Model '{model_name}' not found",
                                "available_models": available_models,
                            }
                        ),
                        404,
                    )

                # Auto-start model if not running (download-once pattern)
                if model_name not in self.active_servers:
                    logger.info(f"Model {model_name} not active, starting...")

                    # Check if model is available on disk
                    if not self.model_manager.is_model_available(model_name):
                        return (
                            jsonify(
                                {
                                    "error": f"Model '{model_name}' not available on filesystem",
                                    "hint": "Use the download endpoint to fetch this model first",
                                }
                            ),
                            503,
                        )

                    # Start the model server
                    try:
                        start_result = self._start_model_server(model_name)
                        if "error" in start_result:
                            return jsonify(start_result), 500
                        logger.info(f"Successfully started model {model_name}")
                    except Exception as e:
                        logger.error(f"Failed to start model {model_name}: {e}")
                        return jsonify({"error": f"Failed to start model: {str(e)}"}), 500

                # Proxy to the active model server using OpenAI chat format
                server_info = self.active_servers[model_name]
                chat_endpoint = server_info["backend"].get_chat_endpoint(server_info["port"])

                # Forward the OpenAI-compatible request
                response = requests.post(
                    chat_endpoint,
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                    timeout=60,
                    stream=stream,
                )

                if stream:
                    # Handle streaming response
                    return Response(
                        response.iter_content(chunk_size=1024),
                        status=response.status_code,
                        headers={
                            "Content-Type": "text/plain; charset=utf-8",
                            "Cache-Control": "no-cache",
                            "Connection": "keep-alive",
                        },
                    )
                else:
                    # Handle non-streaming response
                    return Response(
                        response.content,
                        status=response.status_code,
                        headers={"Content-Type": "application/json"},
                    )

            except Exception as e:
                logger.error(f"Error in chat completions: {e}")
                return jsonify({"error": "Internal server error"}), 500

    def _start_model_server(self, model_name: str) -> dict[str, Any]:
        """Start a server process for the given model"""
        if model_name in self.active_servers:
            return {"error": "Model server already active", "active": True}

        model_info = self.model_manager.get_model_info(model_name)
        if not model_info:
            raise ValueError(f"Model {model_name} not found")

        if not self.model_manager.is_model_available(model_name):
            raise ValueError(f"Model {model_name} not available on filesystem")

        # Get backend for this model
        backend = get_backend_for_model(model_info, self.model_manager.backends)
        if not backend:
            raise ValueError(f"No suitable backend for model {model_name}")

        # Allocate port
        port = self._allocate_port()

        # Get model path
        model_path = self.model_manager.get_model_path(model_name)
        if not Path(model_path).is_absolute():
            model_path = self.model_manager.models_dir / model_path

        # Start server process
        process = backend.start_server(str(model_path), port)

        # Store server info
        self.active_servers[model_name] = {
            "process": process,
            "port": port,
            "backend": backend,
            "started_at": time.time(),
        }

        logger.info(f"Started {model_name} on port {port} with {backend.name}")

        return {
            "model": model_name,
            "port": port,
            "backend": backend.name,
            "health_endpoint": backend.get_health_endpoint(port),
            "chat_endpoint": backend.get_chat_endpoint(port),
            "active": True,
        }

    def _stop_model_server(self, model_name: str) -> dict[str, Any]:
        """Stop the server process for the given model"""
        if model_name not in self.active_servers:
            return {"error": "Model server not active", "active": False}

        server_info = self.active_servers[model_name]
        process = server_info["process"]

        # Terminate the process
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            logger.warning(f"Force killing {model_name} server")
            process.kill()
            process.wait()

        # Remove from active servers
        del self.active_servers[model_name]

        logger.info(f"Stopped {model_name} server")

        return {"model": model_name, "stopped": True, "active": False}

    def _allocate_port(self) -> int:
        """Allocate an available port for a model server"""
        used_ports = {info["port"] for info in self.active_servers.values()}

        port = self.base_port
        while port in used_ports:
            port += 1

        return port

    def cleanup(self):
        """Clean up all active servers"""
        logger.info("Cleaning up active servers")

        for model_name in list(self.active_servers.keys()):
            try:
                self._stop_model_server(model_name)
            except Exception as e:
                logger.error(f"Error stopping {model_name}: {e}")

    def run(self, host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
        """Run the Flask server"""
        try:
            self.app.run(host=host, port=port, debug=debug)
        finally:
            self.cleanup()


def main():
    """Main entry point for running the server"""
    import argparse

    parser = argparse.ArgumentParser(description="Lamina LLM Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--manifest", default="models.yaml", help="Model manifest path")
    parser.add_argument("--models-dir", default="models", help="Models directory")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Create and run server
    server = LLMServer(args.manifest, args.models_dir)

    print(f"🚀 Starting Lamina LLM Server on {args.host}:{args.port}")
    server.run(args.host, args.port, args.debug)


if __name__ == "__main__":
    main()
