# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Environment Manager

Provides high-level environment management operations including
validation, boundary enforcement, and ritual integration.
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Any

from .config import EnvironmentConfig, get_available_environments, load_environment_config
from .validators import EnvironmentValidationError, validate_environment_config

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """
    Manages environment configurations and operations.

    Provides breath-aware environment management with boundary enforcement
    and ritual integration as specified by the High Council.
    """

    def __init__(self, environments_root: Path | None = None):
        """
        Initialize environment manager.

        Args:
            environments_root: Root directory containing environment configs
        """
        if environments_root is None:
            # Default to project root/environments
            project_root = Path(__file__).parent.parent.parent.parent.parent
            environments_root = project_root / "environments"

        self.environments_root = environments_root
        self._configs: dict[str, EnvironmentConfig] = {}
        self._current_environment: str | None = None

        # Discover available environments
        self._discover_environments()

    def _discover_environments(self):
        """Discover and validate available environments."""
        available_envs = get_available_environments(self.environments_root)

        for env_name in available_envs:
            try:
                config = load_environment_config(
                    env_name, self.environments_root / env_name / "config.yaml"
                )
                validate_environment_config(config)
                self._configs[env_name] = config
                logger.info(f"{config.sigil} Discovered environment: {env_name}")
            except Exception as e:
                logger.error(f"Failed to load environment {env_name}: {e}")

    def get_available_environments(self) -> list[str]:
        """Get list of available environment names."""
        return list(self._configs.keys())

    def get_environment_config(self, environment_name: str) -> EnvironmentConfig:
        """
        Get configuration for specified environment.

        Args:
            environment_name: Name of environment

        Returns:
            EnvironmentConfig instance

        Raises:
            ValueError: If environment not found
        """
        if environment_name not in self._configs:
            available = ", ".join(self._configs.keys())
            raise ValueError(f"Environment '{environment_name}' not found. Available: {available}")

        return self._configs[environment_name]

    def set_current_environment(self, environment_name: str):
        """
        Set the current active environment.

        Args:
            environment_name: Name of environment to activate

        Raises:
            ValueError: If environment not found
        """
        if environment_name not in self._configs:
            raise ValueError(f"Environment '{environment_name}' not found")

        self._current_environment = environment_name
        config = self._configs[environment_name]

        # Set environment variables for breath-aware context
        os.environ["LAMINA_ENVIRONMENT"] = environment_name
        os.environ["LAMINA_SIGIL"] = config.sigil
        os.environ["LAMINA_ENV_TYPE"] = config.type

        logger.info(f"{config.sigil} Activated environment: {environment_name}")

    def get_current_environment(self) -> EnvironmentConfig | None:
        """Get the currently active environment config."""
        if self._current_environment is None:
            return None
        return self._configs.get(self._current_environment)

    def validate_all_environments(self) -> dict[str, bool]:
        """
        Validate all discovered environments.

        Returns:
            Dict mapping environment names to validation status
        """
        results = {}

        for env_name, config in self._configs.items():
            try:
                validate_environment_config(config)
                results[env_name] = True
                logger.info(f"{config.sigil} Environment {env_name} validation passed")
            except EnvironmentValidationError as e:
                results[env_name] = False
                logger.error(f"{config.sigil} Environment {env_name} validation failed: {e}")
            except Exception as e:
                results[env_name] = False
                logger.error(f"{config.sigil} Environment {env_name} validation error: {e}")

        return results

    def get_environment_status(self, environment_name: str) -> dict[str, Any]:
        """
        Get detailed status of an environment.

        Args:
            environment_name: Name of environment

        Returns:
            Status dictionary with validation, services, resources
        """
        if environment_name not in self._configs:
            return {"error": f"Environment '{environment_name}' not found"}

        config = self._configs[environment_name]

        try:
            validate_environment_config(config)
            validation_status = "valid"
            validation_errors = []
        except EnvironmentValidationError as e:
            validation_status = "invalid"
            validation_errors = [str(e)]
        except Exception as e:
            validation_status = "error"
            validation_errors = [str(e)]

        return {
            "name": config.name,
            "sigil": config.sigil,
            "type": config.type,
            "description": config.description,
            "validation": {"status": validation_status, "errors": validation_errors},
            "services": list(config.services.keys()),
            "features": config.features,
            "resources": config.get_resource_limits(),
            "is_current": environment_name == self._current_environment,
        }

    def enforce_environment_boundaries(
        self, target_environment: str, container_labels: dict[str, str] | None = None
    ) -> bool:
        """
        Enforce environment boundary rules per Vesna's guidance.

        Args:
            target_environment: Environment being deployed to
            container_labels: Labels from container/artifact

        Returns:
            True if boundaries are respected, False otherwise
        """
        if target_environment not in self._configs:
            logger.error(f"Unknown target environment: {target_environment}")
            return False

        target_config = self._configs[target_environment]

        # Check container labels if provided (Vesna's requirement)
        if container_labels:
            container_env = container_labels.get("lamina.environment")
            container_sigil = container_labels.get("lamina.sigil")

            if container_env and container_env != target_environment:
                logger.error(
                    f"{target_config.sigil} Boundary violation: Container labeled for '{container_env}' "
                    f"cannot run in '{target_environment}'"
                )
                return False

            if container_sigil and container_sigil != target_config.sigil:
                logger.error(
                    f"{target_config.sigil} Boundary violation: Container sigil '{container_sigil}' "
                    f"doesn't match environment sigil '{target_config.sigil}'"
                )
                return False

        # Production-specific boundary checks
        if target_config.is_production():
            # Production should never run dev/test artifacts
            env_var = os.environ.get("ENV", "").lower()
            if env_var in ["development", "dev", "test"]:
                logger.error(
                    f"{target_config.sigil} Boundary violation: Development/test artifact "
                    f"cannot run in production"
                )
                return False

        logger.info(f"{target_config.sigil} Environment boundary check passed")
        return True

    def perform_sigil_of_passage(self, from_env: str, to_env: str, run_tests: bool = True) -> bool:
        """
        Perform Luna's "sigil of passage" ritual between environments.

        Args:
            from_env: Source environment
            to_env: Target environment
            run_tests: Whether to run test gates

        Returns:
            True if passage is blessed, False otherwise
        """
        if from_env not in self._configs or to_env not in self._configs:
            logger.error(f"Invalid environment transition: {from_env} → {to_env}")
            return False

        from_config = self._configs[from_env]
        to_config = self._configs[to_env]

        logger.info(f"{from_config.sigil} → {to_config.sigil} Beginning sigil of passage...")

        # Test gates (Luna's requirement)
        if run_tests:
            if not self._run_passage_tests(from_env, to_env):
                logger.error(f"{from_config.sigil} → {to_config.sigil} Test gates failed")
                return False

        # Boundary enforcement (Vesna's requirement)
        if not self.enforce_environment_boundaries(to_env):
            logger.error(f"{from_config.sigil} → {to_config.sigil} Boundary enforcement failed")
            return False

        # Symbolic acknowledgment
        logger.info(
            f"{from_config.sigil} → {to_config.sigil} Sigil of passage complete. "
            f"Transformation from {from_env} to {to_env} is blessed."
        )

        return True

    def _run_passage_tests(self, from_env: str, to_env: str) -> bool:
        """
        Run test gates for environment passage.

        Args:
            from_env: Source environment
            to_env: Target environment

        Returns:
            True if tests pass, False otherwise
        """
        from_config = self._configs[from_env]
        self._configs[to_env]

        logger.info(f"{from_config.sigil} Running passage tests...")

        # Environment-specific test requirements
        test_commands = []

        if to_env == "test":
            # Transitioning to test environment
            test_commands = [
                "uv run pytest packages/lamina-core/tests/ -m unit",
                "uv run ruff check packages/",
                "uv run black --check packages/",
            ]
        elif to_env == "production":
            # Transitioning to production (comprehensive)
            test_commands = [
                "uv run pytest packages/lamina-core/tests/ -m unit",
                "uv run pytest packages/lamina-core/tests/ -m integration",
                "uv run ruff check packages/",
                "uv run black --check packages/",
                "uv run bandit -r packages/",
            ]

        # Run test commands
        for cmd in test_commands:
            try:
                logger.info(f"{from_config.sigil} Running: {cmd}")
                result = subprocess.run(cmd.split(), capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error(f"{from_config.sigil} Test failed: {cmd}")
                    logger.error(f"Error: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"{from_config.sigil} Test execution error: {e}")
                return False

        logger.info(f"{from_config.sigil} All passage tests passed")
        return True

    def get_cli_status_message(self, environment_name: str | None = None) -> str:
        """
        Get CLI status message with breath markers.

        Args:
            environment_name: Environment to show status for

        Returns:
            Formatted status message with sigil
        """
        if environment_name is None:
            environment_name = self._current_environment

        if environment_name is None:
            return "❓ No environment active"

        if environment_name not in self._configs:
            return f"❓ Unknown environment: {environment_name}"

        config = self._configs[environment_name]
        status = "active" if environment_name == self._current_environment else "available"

        return f"{config.sigil} Environment {environment_name} ({config.type}) - {status}"
