# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Backend Management - llama.cpp wrapper for GGUF model serving

Provides interface for llama.cpp server with plans to expand to other
backends in the future.
"""

import logging
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class LLMBackend(ABC):
    """Abstract base class for LLM backends"""

    def __init__(self, name: str, config: dict[str, Any]):
        self.name = name
        self.config = config
        self.executable = config.get("executable")
        self.default_args = config.get("default_args", [])

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this backend is available on the system"""
        pass

    @abstractmethod
    def start_server(self, model_path: str, port: int = 8080, **kwargs) -> subprocess.Popen:
        """Start a server process for the given model"""
        pass

    @abstractmethod
    def get_health_endpoint(self, port: int = 8080) -> str:
        """Get the health check endpoint URL"""
        pass

    @abstractmethod
    def get_chat_endpoint(self, port: int = 8080) -> str:
        """Get the chat/completion endpoint URL"""
        pass

    def validate_model(self, model_path: str) -> bool:
        """Validate that the model is compatible with this backend"""
        return Path(model_path).exists()


class LlamaCppBackend(LLMBackend):
    """Backend for llama.cpp server"""

    def is_available(self) -> bool:
        """Check if llama-server is available"""
        try:
            result = subprocess.run([self.executable, "--version"], capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def start_server(self, model_path: str, port: int = 8080, **kwargs) -> subprocess.Popen:
        """Start llama-server process"""
        args = [self.executable, "--model", model_path, "--port", str(port), "--host", "0.0.0.0"]

        # Add default arguments
        args.extend(self.default_args)

        # Add any additional arguments from kwargs
        for key, value in kwargs.items():
            if key.startswith("--"):
                args.extend([key, str(value)])
            elif key.replace("_", "-") not in ["model", "port", "host"]:
                args.extend([f'--{key.replace("_", "-")}', str(value)])

        logger.info(f"Starting llama.cpp server: {' '.join(args)}")
        return subprocess.Popen(args)

    def get_health_endpoint(self, port: int = 8080) -> str:
        return f"http://localhost:{port}/health"

    def get_chat_endpoint(self, port: int = 8080) -> str:
        return f"http://localhost:{port}/v1/chat/completions"

    def validate_model(self, model_path: str) -> bool:
        """Validate GGUF model file"""
        path = Path(model_path)
        return path.exists() and path.suffix.lower() == ".gguf"


# Backend registry - focused on llama.cpp for now
BACKENDS = {"llama.cpp": LlamaCppBackend}


def get_backend_for_model(
    model_info: dict[str, Any], backend_configs: dict[str, Any]
) -> LLMBackend | None:
    """
    Get the appropriate backend instance for a model.

    Args:
        model_info: Model information from manifest
        backend_configs: Backend configurations from manifest

    Returns:
        Configured backend instance or None
    """
    backend_name = model_info.get("backend")
    if not backend_name:
        logger.error("No backend specified for model")
        return None

    if backend_name not in BACKENDS:
        logger.error(f"Unknown backend: {backend_name}")
        return None

    backend_config = backend_configs.get(backend_name, {})
    backend_class = BACKENDS[backend_name]

    try:
        backend = backend_class(backend_name, backend_config)

        if not backend.is_available():
            logger.warning(f"Backend {backend_name} is not available on this system")
            return None

        return backend

    except Exception as e:
        logger.error(f"Failed to create backend {backend_name}: {e}")
        return None


def list_available_backends(backend_configs: dict[str, Any]) -> list[str]:
    """List all backends that are available on the current system"""
    available = []

    for backend_name, backend_class in BACKENDS.items():
        backend_config = backend_configs.get(backend_name, {})
        try:
            backend = backend_class(backend_name, backend_config)
            if backend.is_available():
                available.append(backend_name)
        except Exception as e:
            logger.debug(f"Backend {backend_name} not available: {e}")

    return available


def validate_backend_setup(backend_configs: dict[str, Any]) -> dict[str, Any]:
    """Validate the setup of all configured backends"""
    results = {}

    for backend_name in backend_configs:
        if backend_name in BACKENDS:
            backend_config = backend_configs[backend_name]
            backend_class = BACKENDS[backend_name]

            try:
                backend = backend_class(backend_name, backend_config)
                results[backend_name] = {
                    "available": backend.is_available(),
                    "executable": backend.executable,
                    "config": backend_config,
                }
            except Exception as e:
                results[backend_name] = {
                    "available": False,
                    "error": str(e),
                    "config": backend_config,
                }
        else:
            results[backend_name] = {
                "available": False,
                "error": f"Unknown backend type: {backend_name}",
                "config": backend_configs[backend_name],
            }

    return results
