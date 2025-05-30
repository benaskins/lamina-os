# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Tests for Environment Configuration Module

Tests the environment configuration loading, validation, and management
with breath-aware markers and ritual integration.
"""

from pathlib import Path

import pytest
import yaml

from lamina.environment.config import (
    ENVIRONMENT_SIGILS,
    EnvironmentConfig,
    get_available_environments,
    get_environment_sigil,
    load_environment_config,
    validate_environment_name,
)
from lamina.environment.validators import (
    EnvironmentValidationError,
    validate_environment_config,
    validate_environment_transition,
)


class TestEnvironmentConfig:
    """Test EnvironmentConfig dataclass functionality."""

    def test_environment_config_creation(self):
        """Test creating EnvironmentConfig with minimal data."""
        config = EnvironmentConfig(
            name="test", sigil="🜁", type="containerized", description="Test environment"
        )

        assert config.name == "test"
        assert config.sigil == "🜁"
        assert config.type == "containerized"
        assert config.is_test() is True
        assert config.is_development() is False
        assert config.is_production() is False

    def test_sigil_prefix(self):
        """Test sigil prefix for CLI output."""
        config = EnvironmentConfig(
            name="development", sigil="🜂", type="docker-compose", description="Dev environment"
        )

        assert config.get_sigil_prefix() == "🜂 "

    def test_log_format_with_sigil(self):
        """Test log format includes sigil."""
        config = EnvironmentConfig(
            name="production", sigil="🜄", type="kubernetes", description="Prod environment"
        )

        log_format = config.get_log_format()
        assert "🜄" in log_format
        assert "%(asctime)s" in log_format

    def test_features_support(self):
        """Test feature support checking."""
        config = EnvironmentConfig(
            name="development",
            sigil="🜂",
            type="docker-compose",
            description="Dev environment",
            features={"hot_reload": True, "debug_ports": True, "mtls": False},
        )

        assert config.supports_feature("hot_reload") is True
        assert config.supports_feature("debug_ports") is True
        assert config.supports_feature("mtls") is False
        assert config.supports_feature("nonexistent") is False

    def test_service_config_retrieval(self):
        """Test getting service configuration."""
        services = {
            "lamina-core": {"image": "lamina-core:dev"},
            "chromadb": {"image": "chromadb:latest"},
        }

        config = EnvironmentConfig(
            name="test",
            sigil="🜁",
            type="containerized",
            description="Test environment",
            services=services,
        )

        core_config = config.get_service_config("lamina-core")
        assert core_config["image"] == "lamina-core:dev"

        missing_config = config.get_service_config("nonexistent")
        assert missing_config is None

    def test_post_init_sigil_injection(self):
        """Test that sigils are automatically injected into service environments."""
        services = {
            "lamina-core": {"image": "lamina-core:dev", "environment": {"ENV": "development"}}
        }

        config = EnvironmentConfig(
            name="development",
            sigil="🜂",
            type="docker-compose",
            description="Dev environment",
            services=services,
        )

        # Check that sigil was injected
        service_env = config.services["lamina-core"]["environment"]
        assert service_env["SIGIL"] == "🜂"


class TestEnvironmentConfigLoading:
    """Test environment configuration loading from files."""

    def test_load_valid_config(self, tmp_path):
        """Test loading valid environment configuration."""
        config_data = {
            "environment": {
                "name": "development",
                "sigil": "🜂",
                "type": "docker-compose",
                "description": "Development environment",
            },
            "features": {"hot_reload": True},
            "services": {"lamina-core": {"image": "lamina-core:dev"}},
            "logging": {"level": "debug"},
        }

        config_file = tmp_path / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        config = load_environment_config("development", config_file)

        assert config.name == "development"
        assert config.sigil == "🜂"
        assert config.supports_feature("hot_reload")
        assert "lamina-core" in config.services

    def test_load_nonexistent_config(self):
        """Test loading non-existent configuration file."""
        with pytest.raises(FileNotFoundError):
            load_environment_config("nonexistent", Path("/nonexistent/config.yaml"))

    def test_load_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML configuration."""
        config_file = tmp_path / "config.yaml"
        with open(config_file, "w") as f:
            f.write("invalid: yaml: content: [")

        with pytest.raises(ValueError, match="Invalid YAML"):
            load_environment_config("test", config_file)

    def test_get_available_environments(self, tmp_path):
        """Test discovering available environments."""
        # Create environment directories with configs
        for env in ["development", "test", "production"]:
            env_dir = tmp_path / env
            env_dir.mkdir()

            config_data = {
                "environment": {
                    "name": env,
                    "sigil": ENVIRONMENT_SIGILS[env],
                    "type": "docker-compose",
                    "description": f"{env} environment",
                }
            }

            config_file = env_dir / "config.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config_data, f)

        # Create directory without config (should be ignored)
        (tmp_path / "incomplete").mkdir()

        environments = get_available_environments(tmp_path)

        assert set(environments) == {"development", "test", "production"}
        assert len(environments) == 3

    def test_validate_environment_name(self):
        """Test environment name validation."""
        assert validate_environment_name("development") is True
        assert validate_environment_name("test") is True
        assert validate_environment_name("production") is True
        assert validate_environment_name("invalid") is False
        assert validate_environment_name("") is False

    def test_get_environment_sigil(self):
        """Test getting environment sigils."""
        assert get_environment_sigil("development") == "🜂"
        assert get_environment_sigil("test") == "🜁"
        assert get_environment_sigil("production") == "🜄"
        assert get_environment_sigil("unknown") == "❓"


class TestEnvironmentValidation:
    """Test environment configuration validation."""

    def test_valid_development_config(self):
        """Test validation of valid development configuration."""
        config = EnvironmentConfig(
            name="development",
            sigil="🜂",
            type="docker-compose",
            description="Development environment",
            features={"hot_reload": True, "debug_ports": True},
            services={
                "lamina-core": {
                    "image": "lamina-core:dev",
                    "environment": {"ENV": "development", "SIGIL": "🜂"},
                }
            },
            security={"mtls": False},
            logging={"format": "🜂 [%(asctime)s] %(name)s - %(message)s"},
            resources={"total_memory": "4Gi", "total_cpu": "2"},
        )

        # Should not raise exception
        validate_environment_config(config)

    def test_invalid_config_missing_name(self):
        """Test validation fails for missing name."""
        config = EnvironmentConfig(
            name="",  # Invalid
            sigil="🜂",
            type="docker-compose",
            description="Development environment",
        )

        with pytest.raises(EnvironmentValidationError, match="Environment name is required"):
            validate_environment_config(config)

    def test_invalid_config_wrong_sigil(self):
        """Test validation fails for wrong sigil."""
        config = EnvironmentConfig(
            name="development",
            sigil="🜄",  # Wrong sigil for development
            type="docker-compose",
            description="Development environment",
            services={"lamina-core": {"environment": {"ENV": "development", "SIGIL": "🜄"}}},
        )

        with pytest.raises(EnvironmentValidationError, match="Sigil mismatch"):
            validate_environment_config(config)

    def test_production_security_requirements(self):
        """Test production environment security validation."""
        config = EnvironmentConfig(
            name="production",
            sigil="🜄",
            type="kubernetes",
            description="Production environment",
            features={"auto_scaling": True, "comprehensive_monitoring": True},
            services={
                "lamina-core": {
                    "image": "lamina-core:latest",
                    "environment": {"ENV": "production", "SIGIL": "🜄"},
                }
            },
            security={"mtls": False},  # Should require mtls for production
            resources={"total_memory": "80Gi", "total_cpu": "40"},
        )

        with pytest.raises(
            EnvironmentValidationError, match="Production environment requires mtls"
        ):
            validate_environment_config(config)

    def test_test_environment_requirements(self):
        """Test test environment specific validation."""
        config = EnvironmentConfig(
            name="test",
            sigil="🜁",
            type="containerized",
            description="Test environment",
            features={"isolation": True},  # Missing ephemeral
            services={"lamina-core": {"environment": {"ENV": "test", "SIGIL": "🜁"}}},
            security={"mtls": False},
        )

        with pytest.raises(
            EnvironmentValidationError, match="Test environment should be ephemeral"
        ):
            validate_environment_config(config)

    def test_service_environment_validation(self):
        """Test service environment variable validation."""
        config = EnvironmentConfig(
            name="development",
            sigil="🜂",
            type="docker-compose",
            description="Development environment",
            services={
                "lamina-core": {
                    "image": "lamina-core:dev",
                    "environment": {"ENV": "production", "SIGIL": "🜂"},  # Wrong ENV
                }
            },
            security={"mtls": False},
        )

        with pytest.raises(EnvironmentValidationError, match="ENV mismatch"):
            validate_environment_config(config)


class TestEnvironmentTransitions:
    """Test environment transition validation."""

    def test_valid_transitions(self):
        """Test valid environment transitions."""
        # Development to test
        errors = validate_environment_transition("development", "test")
        assert len(errors) == 0

        # Test to production (preferred path)
        errors = validate_environment_transition("test", "production")
        assert len(errors) == 0

    def test_discouraged_transitions(self):
        """Test transitions that are allowed but discouraged."""
        # Development to production (allowed but warns)
        errors = validate_environment_transition("development", "production")
        assert len(errors) == 1
        assert "test environment" in errors[0]

    def test_invalid_transitions(self):
        """Test invalid environment transitions."""
        # Production to anything (no transitions allowed)
        errors = validate_environment_transition("production", "development")
        assert len(errors) > 0
        assert "Invalid transition" in errors[0]

        # Test to development (not allowed)
        errors = validate_environment_transition("test", "development")
        assert len(errors) > 0
        assert "Invalid transition" in errors[0]

    def test_production_transition_requirements(self):
        """Test production transition requirements."""
        # Direct development to production should be discouraged
        errors = validate_environment_transition("development", "production")
        assert len(errors) == 1  # Should warn about skipping test environment
        assert "test environment" in errors[0]

    def test_unknown_environment_transition(self):
        """Test transition with unknown environments."""
        errors = validate_environment_transition("unknown", "test")
        assert len(errors) > 0
        assert "Unknown source environment" in errors[0]


@pytest.mark.integration
class TestEnvironmentConfigIntegration:
    """Integration tests with actual environment configurations."""

    def test_load_actual_development_config(self):
        """Test loading actual development configuration."""
        try:
            config = load_environment_config("development")

            assert config.name == "development"
            assert config.sigil == "🜂"
            assert config.type == "docker-compose"
            assert config.is_development() is True

            # Should have required services
            assert "lamina-core" in config.services

            # Should support development features
            assert config.supports_feature("hot_reload") is True
            assert config.supports_feature("debug_ports") is True

            # Should pass validation
            validate_environment_config(config)

        except FileNotFoundError:
            pytest.skip("Development environment config not found")

    def test_load_actual_test_config(self):
        """Test loading actual test configuration."""
        try:
            config = load_environment_config("test")

            assert config.name == "test"
            assert config.sigil == "🜁"
            assert config.type == "containerized"
            assert config.is_test() is True

            # Should support test features
            assert config.supports_feature("ephemeral") is True
            assert config.supports_feature("isolation") is True

            # Should pass validation
            validate_environment_config(config)

        except FileNotFoundError:
            pytest.skip("Test environment config not found")

    def test_load_actual_production_config(self):
        """Test loading actual production configuration."""
        try:
            config = load_environment_config("production")

            assert config.name == "production"
            assert config.sigil == "🜄"
            assert config.type == "kubernetes"
            assert config.is_production() is True

            # Should support production features
            assert config.supports_feature("auto_scaling") is True
            assert config.supports_feature("comprehensive_monitoring") is True

            # Should pass validation
            validate_environment_config(config)

        except FileNotFoundError:
            pytest.skip("Production environment config not found")
