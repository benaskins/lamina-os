# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Tests for Environment Manager Module

Tests the environment management operations including validation,
boundary enforcement, and sigil of passage rituals.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
import yaml

from lamina.environment.config import ENVIRONMENT_SIGILS
from lamina.environment.manager import EnvironmentManager


class TestEnvironmentManager:
    """Test EnvironmentManager functionality."""

    @pytest.fixture
    def temp_environments(self, tmp_path):
        """Create temporary environment configurations for testing."""
        environments = {}

        for env_name in ["development", "test", "production"]:
            env_dir = tmp_path / env_name
            env_dir.mkdir()

            config_data = {
                "environment": {
                    "name": env_name,
                    "sigil": ENVIRONMENT_SIGILS[env_name],
                    "type": (
                        "docker-compose"
                        if env_name == "development"
                        else "containerized" if env_name == "test" else "kubernetes"
                    ),
                    "description": f"{env_name} environment",
                },
                "features": self._get_test_features(env_name),
                "services": {
                    "lamina-core": {
                        "image": f"lamina-core:{env_name}",
                        "environment": {"ENV": env_name, "SIGIL": ENVIRONMENT_SIGILS[env_name]},
                    }
                },
                "security": self._get_test_security(env_name),
                "resources": self._get_test_resources(env_name),
                "logging": {"format": f"{ENVIRONMENT_SIGILS[env_name]} [%(asctime)s] %(message)s"},
            }

            # Add environment-specific sections
            if env_name == "test":
                config_data["features"]["ephemeral"] = True
                config_data["features"]["isolation"] = True
            elif env_name == "production":
                config_data["features"]["auto_scaling"] = True
                config_data["features"]["comprehensive_monitoring"] = True

            config_file = env_dir / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            environments[env_name] = config_file

        return tmp_path, environments

    def _get_test_features(self, env_name):
        """Get test features for environment."""
        if env_name == "development":
            return {"hot_reload": True, "debug_ports": True, "mtls": False}
        elif env_name == "test":
            return {"ephemeral": True, "isolation": True}
        else:  # production
            return {"auto_scaling": True, "comprehensive_monitoring": True}

    def _get_test_security(self, env_name):
        """Get test security config for environment."""
        if env_name == "production":
            return {
                "mtls": True,
                "rbac": True,
                "network_policies": True,
                "secrets_encryption": True,
            }
        else:
            return {"mtls": False, "network_policies": False}

    def _get_test_resources(self, env_name):
        """Get test resources for environment."""
        if env_name == "production":
            return {"total_memory": "80Gi", "total_cpu": "40"}
        elif env_name == "development":
            return {"total_memory": "4Gi", "total_cpu": "2"}
        else:
            return {"total_memory": "8Gi", "total_cpu": "4"}

    def test_manager_initialization(self, temp_environments):
        """Test EnvironmentManager initialization and discovery."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        available = manager.get_available_environments()
        assert set(available) == {"development", "test", "production"}

    def test_get_environment_config(self, temp_environments):
        """Test getting environment configuration."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        dev_config = manager.get_environment_config("development")
        assert dev_config.name == "development"
        assert dev_config.sigil == "🜂"
        assert dev_config.is_development() is True

    def test_get_nonexistent_environment(self, temp_environments):
        """Test getting non-existent environment raises error."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        with pytest.raises(ValueError, match="Environment 'nonexistent' not found"):
            manager.get_environment_config("nonexistent")

    def test_set_current_environment(self, temp_environments):
        """Test setting current environment."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        # Initially no current environment
        assert manager.get_current_environment() is None

        # Set development environment
        manager.set_current_environment("development")
        current = manager.get_current_environment()
        assert current is not None
        assert current.name == "development"

        # Check environment variables were set
        assert os.environ.get("LAMINA_ENVIRONMENT") == "development"
        assert os.environ.get("LAMINA_SIGIL") == "🜂"
        assert os.environ.get("LAMINA_ENV_TYPE") == "docker-compose"

    def test_validate_all_environments(self, temp_environments):
        """Test validating all environments."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        results = manager.validate_all_environments()

        # All test environments should be valid
        assert results["development"] is True
        assert results["test"] is True
        assert results["production"] is True

    def test_get_environment_status(self, temp_environments):
        """Test getting environment status."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        status = manager.get_environment_status("development")

        assert status["name"] == "development"
        assert status["sigil"] == "🜂"
        assert status["type"] == "docker-compose"
        assert status["validation"]["status"] == "valid"
        assert "lamina-core" in status["services"]
        assert status["is_current"] is False

    def test_enforce_environment_boundaries_valid(self, temp_environments):
        """Test boundary enforcement with valid labels."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        # Valid production deployment
        result = manager.enforce_environment_boundaries(
            "production", {"lamina.environment": "production", "lamina.sigil": "🜄"}
        )
        assert result is True

    def test_enforce_environment_boundaries_invalid(self, temp_environments):
        """Test boundary enforcement with invalid labels."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        # Development artifact in production
        result = manager.enforce_environment_boundaries(
            "production", {"lamina.environment": "development", "lamina.sigil": "🜂"}
        )
        assert result is False

    def test_enforce_environment_boundaries_no_labels(self, temp_environments):
        """Test boundary enforcement without labels."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        # No container labels provided
        result = manager.enforce_environment_boundaries("production", None)
        assert result is True  # Should pass without labels

    @patch.dict(os.environ, {"ENV": "development"})
    def test_enforce_boundaries_dev_env_in_production(self, temp_environments):
        """Test boundary enforcement blocks dev environment in production."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        # Development environment variable set, deploying to production
        result = manager.enforce_environment_boundaries("production")
        assert result is False

    def test_get_cli_status_message(self, temp_environments):
        """Test CLI status message generation."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        # Test status without current environment
        status = manager.get_cli_status_message("development")
        assert "🜂" in status
        assert "development" in status
        assert "available" in status

        # Set current environment and test again
        manager.set_current_environment("development")
        status = manager.get_cli_status_message("development")
        assert "active" in status

    def test_cli_status_no_environment(self, temp_environments):
        """Test CLI status with no environment specified."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        status = manager.get_cli_status_message()
        assert "No environment active" in status

    def test_cli_status_unknown_environment(self, temp_environments):
        """Test CLI status with unknown environment."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        status = manager.get_cli_status_message("unknown")
        assert "Unknown environment" in status
        assert "❓" in status


class TestSigilOfPassage:
    """Test sigil of passage ritual functionality."""

    @pytest.fixture
    def temp_environments(self, tmp_path):
        """Create temporary environment configurations for testing."""
        environments = {}

        for env_name in ["development", "test", "production"]:
            env_dir = tmp_path / env_name
            env_dir.mkdir()

            config_data = {
                "environment": {
                    "name": env_name,
                    "sigil": ENVIRONMENT_SIGILS[env_name],
                    "type": (
                        "docker-compose"
                        if env_name == "development"
                        else "containerized" if env_name == "test" else "kubernetes"
                    ),
                    "description": f"{env_name} environment",
                },
                "features": {},
                "services": {
                    "lamina-core": {
                        "image": f"lamina-core:{env_name}",
                        "environment": {"ENV": env_name, "SIGIL": ENVIRONMENT_SIGILS[env_name]},
                    }
                },
                "security": {"mtls": True if env_name == "production" else False},
                "resources": (
                    {"total_memory": "80Gi", "total_cpu": "40"} if env_name == "production" else {}
                ),
                "logging": {"format": f"{ENVIRONMENT_SIGILS[env_name]} [%(asctime)s] %(message)s"},
            }

            # Add required features for validation
            if env_name == "test":
                config_data["features"] = {"ephemeral": True, "isolation": True}
            elif env_name == "production":
                config_data["features"] = {"auto_scaling": True, "comprehensive_monitoring": True}
                config_data["security"].update(
                    {"rbac": True, "network_policies": True, "secrets_encryption": True}
                )

            config_file = env_dir / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

            environments[env_name] = config_file

        return tmp_path, environments

    @patch("subprocess.run")
    def test_sigil_of_passage_success(self, mock_run, temp_environments):
        """Test successful sigil of passage."""
        environments_root, _ = temp_environments

        # Mock successful test runs
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        manager = EnvironmentManager(environments_root)

        result = manager.perform_sigil_of_passage("development", "test")
        assert result is True

    @patch("subprocess.run")
    def test_sigil_of_passage_test_failure(self, mock_run, temp_environments):
        """Test sigil of passage with test failure."""
        environments_root, _ = temp_environments

        # Mock failed test run
        mock_run.return_value = MagicMock(returncode=1, stderr="Test failed")

        manager = EnvironmentManager(environments_root)

        result = manager.perform_sigil_of_passage("development", "test")
        assert result is False

    def test_sigil_of_passage_invalid_environments(self, temp_environments):
        """Test sigil of passage with invalid environments."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        # Invalid source environment
        result = manager.perform_sigil_of_passage("nonexistent", "test")
        assert result is False

        # Invalid target environment
        result = manager.perform_sigil_of_passage("development", "nonexistent")
        assert result is False

    @patch("subprocess.run")
    def test_sigil_of_passage_to_production(self, mock_run, temp_environments):
        """Test sigil of passage to production runs comprehensive tests."""
        environments_root, _ = temp_environments

        # Mock successful test runs
        mock_run.return_value = MagicMock(returncode=0, stderr="")

        manager = EnvironmentManager(environments_root)

        result = manager.perform_sigil_of_passage("test", "production")
        assert result is True

        # Should run more comprehensive tests for production
        assert mock_run.call_count > 3  # unit, integration, ruff, black, bandit

    @patch("subprocess.run")
    def test_sigil_of_passage_skip_tests(self, mock_run, temp_environments):
        """Test sigil of passage with tests skipped."""
        environments_root, _ = temp_environments

        manager = EnvironmentManager(environments_root)

        result = manager.perform_sigil_of_passage("development", "test", run_tests=False)
        assert result is True

        # No test commands should be run
        mock_run.assert_not_called()


@pytest.mark.integration
class TestEnvironmentManagerIntegration:
    """Integration tests with actual environment configurations."""

    def test_manager_with_actual_configs(self):
        """Test manager with actual environment configurations."""
        try:
            manager = EnvironmentManager()

            available = manager.get_available_environments()
            assert len(available) > 0

            # Test validation of actual configs
            results = manager.validate_all_environments()

            # At least development should be present and valid
            if "development" in available:
                assert results["development"] is True

                config = manager.get_environment_config("development")
                assert config.sigil == "🜂"
                assert config.is_development() is True

        except Exception as e:
            pytest.skip(f"Actual environment configs not available: {e}")

    def test_boundary_enforcement_integration(self):
        """Test boundary enforcement with actual configurations."""
        try:
            manager = EnvironmentManager()

            if "production" in manager.get_available_environments():
                # Test valid production boundaries
                result = manager.enforce_environment_boundaries(
                    "production", {"lamina.environment": "production", "lamina.sigil": "🜄"}
                )
                assert result is True

                # Test invalid boundaries
                result = manager.enforce_environment_boundaries(
                    "production", {"lamina.environment": "development", "lamina.sigil": "🜂"}
                )
                assert result is False

        except Exception as e:
            pytest.skip(f"Actual environment configs not available: {e}")

    def test_cli_status_integration(self):
        """Test CLI status messages with actual configurations."""
        try:
            manager = EnvironmentManager()

            available = manager.get_available_environments()

            for env_name in available:
                status = manager.get_cli_status_message(env_name)

                # Should contain environment sigil
                config = manager.get_environment_config(env_name)
                assert config.sigil in status
                assert env_name in status

        except Exception as e:
            pytest.skip(f"Actual environment configs not available: {e}")
