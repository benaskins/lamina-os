# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Tests for Helm Chart Generator

Tests the Helm chart generation functionality for GitOps deployments
including chart structure, templates, and validation.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from lamina.environment.config import EnvironmentConfig
from lamina.environment.helm import HelmChartGenerator, HelmError


class TestHelmChartGenerator:
    """Test Helm chart generation functionality."""

    @pytest.fixture
    def production_config(self):
        """Create production environment configuration for testing."""
        return EnvironmentConfig(
            name="production",
            sigil="🜄",
            type="kubernetes",
            description="Production environment",
            features={
                "auto_scaling": True,
                "comprehensive_monitoring": True,
            },
            services={
                "lamina-core": {
                    "image": "lamina-core:latest",
                    "replicas": 3,
                    "ports": [8080],
                    "environment": {"ENV": "production", "SIGIL": "🜄"},
                    "resources": {
                        "requests": {"memory": "1Gi", "cpu": "500m"},
                        "limits": {"memory": "2Gi", "cpu": "1"},
                    },
                },
                "chromadb": {
                    "image": "chromadb/chroma:latest",
                    "replicas": 1,
                    "ports": [8000],
                    "environment": {"ENV": "production", "SIGIL": "🜄"},
                    "resources": {
                        "requests": {"memory": "2Gi", "cpu": "1"},
                        "limits": {"memory": "4Gi", "cpu": "2"},
                    },
                },
            },
            autoscaling={
                "lamina-core": {
                    "min_replicas": 2,
                    "max_replicas": 10,
                    "target_cpu": 70,
                }
            },
            monitoring={
                "prometheus": {"enabled": True},
                "grafana": {"enabled": True},
            },
            security={
                "mtls": True,
                "rbac": True,
                "network_policies": True,
                "secrets_encryption": True,
            },
            resources={"total_memory": "80Gi", "total_cpu": "40"},
        )

    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @patch("subprocess.run")
    def test_helm_validation_success(self, mock_run, production_config, temp_output_dir):
        """Test successful Helm validation."""
        # Mock helm version command
        mock_run.return_value = MagicMock(returncode=0, stdout="v3.14.0+g7cc8f45", stderr="")

        generator = HelmChartGenerator(production_config, temp_output_dir)
        assert generator.config.name == "production"
        assert generator.chart_name == "lamina-production"

    @patch("subprocess.run")
    def test_helm_not_available(self, mock_run, production_config, temp_output_dir):
        """Test error when Helm is not available."""
        mock_run.side_effect = FileNotFoundError("helm not found")

        with pytest.raises(HelmError, match="Helm not available"):
            HelmChartGenerator(production_config, temp_output_dir)

    @patch("subprocess.run")
    def test_generate_chart_structure(self, mock_run, production_config, temp_output_dir):
        """Test chart structure generation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="v3.14.0", stderr="")

        generator = HelmChartGenerator(production_config, temp_output_dir)
        chart_dir = generator.generate_chart()

        # Check chart directory structure
        assert chart_dir.exists()
        assert (chart_dir / "Chart.yaml").exists()
        assert (chart_dir / "values.yaml").exists()
        assert (chart_dir / "templates").exists()
        assert (chart_dir / "templates" / "_helpers.tpl").exists()

        # Check generated files
        expected_files = [
            "namespace.yaml",
            "serviceaccount.yaml",
            "rbac.yaml",
            "hpa.yaml",
            "networkpolicy.yaml",
        ]
        for file_name in expected_files:
            assert (chart_dir / "templates" / file_name).exists()

        # Check service-specific files
        for service_name in ["lamina-core", "chromadb"]:
            assert (chart_dir / "templates" / f"{service_name}-deployment.yaml").exists()
            assert (chart_dir / "templates" / f"{service_name}-service.yaml").exists()

    @patch("subprocess.run")
    def test_chart_yaml_generation(self, mock_run, production_config, temp_output_dir):
        """Test Chart.yaml generation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="v3.14.0", stderr="")

        generator = HelmChartGenerator(production_config, temp_output_dir)
        chart_dir = generator.generate_chart()

        # Load and validate Chart.yaml
        chart_yaml_path = chart_dir / "Chart.yaml"
        with open(chart_yaml_path) as f:
            chart_data = yaml.safe_load(f)

        assert chart_data["name"] == "lamina-production"
        assert chart_data["version"] == "1.0.0"
        assert chart_data["type"] == "application"
        assert chart_data["annotations"]["lamina.environment"] == "production"
        assert chart_data["annotations"]["lamina.sigil"] == "🜄"
        assert "Lamina High Council" in str(chart_data["maintainers"])

    @patch("subprocess.run")
    def test_values_yaml_generation(self, mock_run, production_config, temp_output_dir):
        """Test values.yaml generation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="v3.14.0", stderr="")

        generator = HelmChartGenerator(production_config, temp_output_dir)
        chart_dir = generator.generate_chart()

        # Load and validate values.yaml
        values_path = chart_dir / "values.yaml"
        with open(values_path) as f:
            values_data = yaml.safe_load(f)

        # Check global configuration
        assert values_data["global"]["environment"] == "production"
        assert values_data["global"]["sigil"] == "🜄"
        assert values_data["global"]["namespace"] == "lamina-production"

        # Check service configurations
        assert "lamina-core" in values_data["services"]
        assert "chromadb" in values_data["services"]

        # Check lamina-core service config
        core_config = values_data["services"]["lamina-core"]
        assert core_config["enabled"] is True
        assert core_config["replicaCount"] == 3
        assert core_config["service"]["ports"] == [8080]
        assert core_config["resources"]["requests"]["memory"] == "1Gi"

        # Check autoscaling configuration
        assert values_data["autoscaling"]["enabled"] is True
        assert "lamina-core" in values_data["autoscaling"]["configs"]
        assert values_data["autoscaling"]["configs"]["lamina-core"]["minReplicas"] == 2

        # Check monitoring configuration
        assert values_data["monitoring"]["enabled"] is True
        assert values_data["monitoring"]["prometheus"]["enabled"] is True

        # Check security configuration
        assert values_data["security"]["networkPolicies"]["enabled"] is True
        assert values_data["security"]["mtls"]["enabled"] is True

    @patch("subprocess.run")
    def test_deployment_template_generation(self, mock_run, production_config, temp_output_dir):
        """Test deployment template generation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="v3.14.0", stderr="")

        generator = HelmChartGenerator(production_config, temp_output_dir)
        chart_dir = generator.generate_chart()

        # Check deployment template for lamina-core
        deployment_template = chart_dir / "templates" / "lamina-core-deployment.yaml"
        assert deployment_template.exists()

        content = deployment_template.read_text()
        assert "{{- if .Values.services.lamina-core.enabled }}" in content
        assert "app.kubernetes.io/component: lamina-core" in content
        assert "serviceAccountName: {{ .Values.serviceAccount.name }}" in content
        assert "LAMINA_ENVIRONMENT" in content
        assert "LAMINA_SIGIL" in content
        assert "securityContext:" in content

    @patch("subprocess.run")
    def test_service_template_generation(self, mock_run, production_config, temp_output_dir):
        """Test service template generation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="v3.14.0", stderr="")

        generator = HelmChartGenerator(production_config, temp_output_dir)
        chart_dir = generator.generate_chart()

        # Check service template for lamina-core
        service_template = chart_dir / "templates" / "lamina-core-service.yaml"
        assert service_template.exists()

        content = service_template.read_text()
        assert "{{- if .Values.services.lamina-core.enabled }}" in content
        assert "name: lamina-core" in content
        assert "app.kubernetes.io/component: lamina-core" in content

    @patch("subprocess.run")
    def test_hpa_template_generation(self, mock_run, production_config, temp_output_dir):
        """Test HorizontalPodAutoscaler template generation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="v3.14.0", stderr="")

        generator = HelmChartGenerator(production_config, temp_output_dir)
        chart_dir = generator.generate_chart()

        # Check HPA template
        hpa_template = chart_dir / "templates" / "hpa.yaml"
        assert hpa_template.exists()

        content = hpa_template.read_text()
        assert "{{- if .Values.autoscaling.enabled }}" in content
        assert "HorizontalPodAutoscaler" in content
        assert "{{ $serviceName }}-hpa" in content

    @patch("subprocess.run")
    def test_rbac_template_generation(self, mock_run, production_config, temp_output_dir):
        """Test RBAC template generation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="v3.14.0", stderr="")

        generator = HelmChartGenerator(production_config, temp_output_dir)
        chart_dir = generator.generate_chart()

        # Check RBAC template
        rbac_template = chart_dir / "templates" / "rbac.yaml"
        assert rbac_template.exists()

        content = rbac_template.read_text()
        assert "{{- if .Values.rbac.create }}" in content
        assert "Role" in content
        assert "RoleBinding" in content
        assert "{{ .Values.serviceAccount.name }}" in content

    @patch("subprocess.run")
    def test_gitops_configs_generation(self, mock_run, production_config, temp_output_dir):
        """Test GitOps configuration files generation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="v3.14.0", stderr="")

        generator = HelmChartGenerator(production_config, temp_output_dir)
        chart_dir = generator.generate_chart()

        # Check GitHub workflow
        workflow_dir = chart_dir / ".github" / "workflows"
        assert workflow_dir.exists()
        workflow_file = workflow_dir / "deploy-production.yml"
        assert workflow_file.exists()

        workflow_content = workflow_file.read_text()
        assert "Deploy Production Environment" in workflow_content
        assert "environment: production" in workflow_content
        assert "🜄" in workflow_content
        assert "helm upgrade --install" in workflow_content

        # Check ArgoCD application
        argocd_file = chart_dir / "argocd-application.yaml"
        assert argocd_file.exists()

        with open(argocd_file) as f:
            argocd_data = yaml.safe_load(f)

        assert argocd_data["kind"] == "Application"
        assert argocd_data["metadata"]["name"] == "lamina-production"
        assert argocd_data["metadata"]["labels"]["lamina.environment"] == "production"
        assert argocd_data["spec"]["source"]["path"] == "charts/lamina-production"

    @patch("subprocess.run")
    def test_helpers_template_generation(self, mock_run, production_config, temp_output_dir):
        """Test _helpers.tpl template generation."""
        mock_run.return_value = MagicMock(returncode=0, stdout="v3.14.0", stderr="")

        generator = HelmChartGenerator(production_config, temp_output_dir)
        chart_dir = generator.generate_chart()

        # Check helpers template
        helpers_template = chart_dir / "templates" / "_helpers.tpl"
        assert helpers_template.exists()

        content = helpers_template.read_text()
        assert "lamina.name" in content
        assert "lamina.fullname" in content
        assert "lamina.labels" in content
        assert "lamina.selectorLabels" in content

    @patch("subprocess.run")
    def test_chart_validation_success(self, mock_run, production_config, temp_output_dir):
        """Test successful chart validation."""
        # Mock helm commands
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="v3.14.0", stderr=""),  # version check
            MagicMock(returncode=0, stdout="", stderr=""),  # lint
            MagicMock(returncode=0, stdout="", stderr=""),  # template dry-run
        ]

        generator = HelmChartGenerator(production_config, temp_output_dir)
        generator.generate_chart()

        result = generator.validate_chart()
        assert result is True

        # Verify helm commands were called
        assert mock_run.call_count == 3

    @patch("subprocess.run")
    def test_chart_validation_failure(self, mock_run, production_config, temp_output_dir):
        """Test chart validation failure."""
        import subprocess

        # Mock helm commands with lint failure - need enough calls for both generation and validation
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="v3.14.0", stderr=""),  # version check (init)
            subprocess.CalledProcessError(1, ["helm", "lint"], stderr="lint error"),  # lint failure
        ]

        generator = HelmChartGenerator(production_config, temp_output_dir)
        generator.generate_chart()

        result = generator.validate_chart()
        assert result is False

    @patch("subprocess.run")
    def test_chart_packaging(self, mock_run, production_config, temp_output_dir):
        """Test chart packaging."""
        # Mock helm commands
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="v3.14.0", stderr=""),  # version check
            MagicMock(
                returncode=0,
                stdout="Successfully packaged chart and saved it to: /tmp/lamina-production-1.0.0.tgz",
                stderr="",
            ),  # package
        ]

        generator = HelmChartGenerator(production_config, temp_output_dir)
        generator.generate_chart()

        package_path = generator.package_chart()
        assert package_path == Path("/tmp/lamina-production-1.0.0.tgz")

    @patch("subprocess.run")
    def test_chart_packaging_failure(self, mock_run, production_config, temp_output_dir):
        """Test chart packaging failure."""
        import subprocess

        # Mock helm commands with package failure
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="v3.14.0", stderr=""),  # version check (init)
            subprocess.CalledProcessError(
                1, ["helm", "package"], stderr="package error"
            ),  # package failure
        ]

        generator = HelmChartGenerator(production_config, temp_output_dir)
        generator.generate_chart()

        with pytest.raises(HelmError, match="Failed to package chart"):
            generator.package_chart()

    def test_non_production_config_rejection(self, temp_output_dir):
        """Test rejection of non-production environments."""
        dev_config = EnvironmentConfig(
            name="development",
            sigil="🜂",
            type="docker-compose",
            description="Development environment",
        )

        with pytest.raises(ValueError, match="only supports production environments"):
            HelmChartGenerator(dev_config, temp_output_dir)


class TestHelmChartIntegration:
    """Integration tests for Helm chart generation."""

    @pytest.fixture
    def real_production_config(self):
        """Load real production configuration for testing."""
        try:
            from lamina.environment.config import load_environment_config

            return load_environment_config("production")
        except FileNotFoundError:
            pytest.skip("Production environment configuration not found")

    @patch("subprocess.run")
    def test_real_config_chart_generation(self, mock_run, real_production_config, tmp_path):
        """Test chart generation with real production configuration."""
        mock_run.return_value = MagicMock(returncode=0, stdout="v3.14.0", stderr="")

        generator = HelmChartGenerator(real_production_config, tmp_path)
        chart_dir = generator.generate_chart()

        # Verify chart structure
        assert chart_dir.exists()
        assert (chart_dir / "Chart.yaml").exists()
        assert (chart_dir / "values.yaml").exists()

        # Load and basic validation of generated files
        with open(chart_dir / "Chart.yaml") as f:
            chart_data = yaml.safe_load(f)
        assert chart_data["name"] == "lamina-production"

        with open(chart_dir / "values.yaml") as f:
            values_data = yaml.safe_load(f)
        assert values_data["global"]["environment"] == "production"

    @patch("subprocess.run")
    def test_complete_gitops_workflow(self, mock_run, real_production_config, tmp_path):
        """Test complete GitOps workflow: generate, validate, package."""
        # Mock all helm commands successfully
        mock_run.side_effect = [
            MagicMock(returncode=0, stdout="v3.14.0", stderr=""),  # version
            MagicMock(returncode=0, stdout="", stderr=""),  # lint
            MagicMock(returncode=0, stdout="", stderr=""),  # template
            MagicMock(
                returncode=0,
                stdout="Successfully packaged chart and saved it to: /tmp/lamina-production-1.0.0.tgz",
                stderr="",
            ),  # package
        ]

        generator = HelmChartGenerator(real_production_config, tmp_path)

        # Generate chart
        chart_dir = generator.generate_chart()
        assert chart_dir.exists()

        # Validate chart
        assert generator.validate_chart() is True

        # Package chart
        package_path = generator.package_chart()
        assert str(package_path).endswith("lamina-production-1.0.0.tgz")

        # Verify all expected files exist
        expected_files = [
            "Chart.yaml",
            "values.yaml",
            "templates/_helpers.tpl",
            "templates/namespace.yaml",
            ".github/workflows/deploy-production.yml",
            "argocd-application.yaml",
        ]

        for file_path in expected_files:
            assert (chart_dir / file_path).exists()
