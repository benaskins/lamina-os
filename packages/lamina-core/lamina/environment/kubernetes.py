# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Kubernetes Deployment Orchestrator

Provides comprehensive Kubernetes deployment capabilities with breath-aware
environment management and production-ready cluster operations.
"""

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import yaml

from .config import EnvironmentConfig

logger = logging.getLogger(__name__)


class KubernetesError(Exception):
    """Raised when Kubernetes operations fail."""

    pass


class KubernetesOrchestrator:
    """
    Orchestrates Kubernetes deployments with breath-aware environment management.

    Provides production-ready deployment capabilities including namespace management,
    RBAC setup, service mesh integration, and monitoring configuration.
    """

    def __init__(self, config: EnvironmentConfig, kubeconfig_path: Path | None = None):
        """
        Initialize Kubernetes orchestrator.

        Args:
            config: Environment configuration for deployment
            kubeconfig_path: Path to kubeconfig file
        """
        if not config.is_production():
            raise ValueError("Kubernetes orchestrator only supports production environments")

        self.config = config
        self.kubeconfig_path = kubeconfig_path
        self.namespace = f"lamina-{config.name}"

        # Validate kubectl availability
        self._validate_kubectl()

    def _validate_kubectl(self):
        """Validate kubectl is available and functional."""
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client", "--output=json"],
                capture_output=True,
                text=True,
                check=True,
            )
            client_info = json.loads(result.stdout)
            logger.info(
                f"{self.config.sigil} kubectl client version: {client_info['clientVersion']['gitVersion']}"
            )
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
            raise KubernetesError(f"kubectl not available or not functional: {e}")

        # Test cluster connectivity
        try:
            self._run_kubectl(["cluster-info", "--request-timeout=10s"])
            logger.info(f"{self.config.sigil} Kubernetes cluster connectivity verified")
        except subprocess.CalledProcessError as e:
            raise KubernetesError(f"Cannot connect to Kubernetes cluster: {e.stderr}")

    def _run_kubectl(self, args: list[str], check: bool = True) -> subprocess.CompletedProcess:
        """
        Run kubectl command with environment configuration.

        Args:
            args: kubectl command arguments
            check: Whether to raise exception on non-zero exit

        Returns:
            CompletedProcess result
        """
        cmd = ["kubectl"]
        if self.kubeconfig_path:
            cmd.extend(["--kubeconfig", str(self.kubeconfig_path)])
        cmd.extend(args)

        logger.debug(f"{self.config.sigil} Running: {' '.join(cmd)}")

        return subprocess.run(cmd, capture_output=True, text=True, check=check)

    def create_namespace(self) -> bool:
        """
        Create and configure namespace for Lamina deployment.

        Returns:
            True if namespace was created or already exists
        """
        logger.info(f"{self.config.sigil} Creating namespace: {self.namespace}")

        # Check if namespace exists
        result = self._run_kubectl(["get", "namespace", self.namespace], check=False)
        if result.returncode == 0:
            logger.info(f"{self.config.sigil} Namespace {self.namespace} already exists")
            return True

        # Create namespace with labels
        namespace_yaml = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self.namespace,
                "labels": {
                    "lamina.environment": self.config.name,
                    "lamina.sigil": self.config.sigil,
                    "lamina.type": self.config.type,
                    "app.kubernetes.io/name": "lamina-os",
                    "app.kubernetes.io/part-of": "lamina-constellation",
                },
                "annotations": {
                    "lamina.description": self.config.description,
                    "lamina.managed-by": "lamina-core",
                },
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(namespace_yaml, f)
            namespace_file = f.name

        try:
            self._run_kubectl(["apply", "-f", namespace_file])
            logger.info(f"{self.config.sigil} Namespace {self.namespace} created successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{self.config.sigil} Failed to create namespace: {e.stderr}")
            return False
        finally:
            Path(namespace_file).unlink(missing_ok=True)

    def setup_rbac(self) -> bool:
        """
        Setup RBAC for Lamina services.

        Returns:
            True if RBAC was configured successfully
        """
        logger.info(f"{self.config.sigil} Setting up RBAC for namespace: {self.namespace}")

        # Service account for Lamina services
        service_account = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": "lamina-service-account",
                "namespace": self.namespace,
                "labels": {
                    "lamina.environment": self.config.name,
                    "lamina.sigil": self.config.sigil,
                },
            },
        }

        # Role for Lamina operations
        role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": "lamina-role",
                "namespace": self.namespace,
                "labels": {
                    "lamina.environment": self.config.name,
                    "lamina.sigil": self.config.sigil,
                },
            },
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["pods", "services", "configmaps", "secrets"],
                    "verbs": ["get", "list", "watch", "create", "update", "patch"],
                },
                {
                    "apiGroups": ["apps"],
                    "resources": ["deployments"],
                    "verbs": ["get", "list", "watch", "create", "update", "patch"],
                },
            ],
        }

        # Role binding
        role_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": "lamina-role-binding",
                "namespace": self.namespace,
                "labels": {
                    "lamina.environment": self.config.name,
                    "lamina.sigil": self.config.sigil,
                },
            },
            "subjects": [
                {
                    "kind": "ServiceAccount",
                    "name": "lamina-service-account",
                    "namespace": self.namespace,
                }
            ],
            "roleRef": {
                "kind": "Role",
                "name": "lamina-role",
                "apiGroup": "rbac.authorization.k8s.io",
            },
        }

        rbac_resources = [service_account, role, role_binding]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            for i, resource in enumerate(rbac_resources):
                if i > 0:
                    f.write("---\n")
                yaml.dump(resource, f)
            rbac_file = f.name

        try:
            self._run_kubectl(["apply", "-f", rbac_file])
            logger.info(f"{self.config.sigil} RBAC configured successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{self.config.sigil} Failed to setup RBAC: {e.stderr}")
            return False
        finally:
            Path(rbac_file).unlink(missing_ok=True)

    def deploy_service(self, service_name: str, service_config: dict[str, Any]) -> bool:
        """
        Deploy a service to Kubernetes.

        Args:
            service_name: Name of the service
            service_config: Service configuration from environment config

        Returns:
            True if deployment was successful
        """
        logger.info(f"{self.config.sigil} Deploying service: {service_name}")

        # Generate deployment and service manifests
        deployment = self._generate_deployment(service_name, service_config)
        service = self._generate_service(service_name, service_config)

        manifests = [deployment, service]

        # Add ConfigMap if configuration is specified
        if "config" in service_config:
            config_map = self._generate_configmap(service_name, service_config["config"])
            manifests.append(config_map)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            for i, manifest in enumerate(manifests):
                if i > 0:
                    f.write("---\n")
                yaml.dump(manifest, f)
            manifest_file = f.name

        try:
            self._run_kubectl(["apply", "-f", manifest_file])
            logger.info(f"{self.config.sigil} Service {service_name} deployed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{self.config.sigil} Failed to deploy service {service_name}: {e.stderr}")
            return False
        finally:
            Path(manifest_file).unlink(missing_ok=True)

    def _generate_deployment(
        self, service_name: str, service_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate Kubernetes Deployment manifest."""
        # Extract resource requirements
        resources = service_config.get("resources", {})

        # Convert Lamina resource format to Kubernetes format
        k8s_resources = {}
        if "requests" in resources or "limits" in resources:
            k8s_resources = resources
        else:
            # Default resource allocation for production
            k8s_resources = {
                "requests": {"memory": "512Mi", "cpu": "250m"},
                "limits": {"memory": "1Gi", "cpu": "500m"},
            }

        # Environment variables
        env_vars = []
        env_config = service_config.get("environment", {})
        for key, value in env_config.items():
            env_vars.append({"name": key, "value": str(value)})

        # Add Lamina-specific environment variables
        env_vars.extend(
            [
                {"name": "LAMINA_ENVIRONMENT", "value": self.config.name},
                {"name": "LAMINA_SIGIL", "value": self.config.sigil},
                {"name": "LAMINA_NAMESPACE", "value": self.namespace},
            ]
        )

        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": service_name,
                "namespace": self.namespace,
                "labels": {
                    "app": service_name,
                    "lamina.environment": self.config.name,
                    "lamina.sigil": self.config.sigil,
                    "app.kubernetes.io/name": service_name,
                    "app.kubernetes.io/part-of": "lamina-constellation",
                },
            },
            "spec": {
                "replicas": service_config.get("replicas", 1),
                "selector": {"matchLabels": {"app": service_name}},
                "template": {
                    "metadata": {
                        "labels": {
                            "app": service_name,
                            "lamina.environment": self.config.name,
                            "lamina.sigil": self.config.sigil,
                        }
                    },
                    "spec": {
                        "serviceAccountName": "lamina-service-account",
                        "containers": [
                            {
                                "name": service_name,
                                "image": service_config.get("image", f"{service_name}:latest"),
                                "ports": [
                                    {"containerPort": port}
                                    for port in service_config.get("ports", [8080])
                                ],
                                "env": env_vars,
                                "resources": k8s_resources,
                                "securityContext": {
                                    "allowPrivilegeEscalation": False,
                                    "runAsNonRoot": True,
                                    "readOnlyRootFilesystem": True,
                                    "capabilities": {"drop": ["ALL"]},
                                },
                            }
                        ],
                        "securityContext": {
                            "fsGroup": 1000,
                            "runAsUser": 1000,
                            "runAsGroup": 1000,
                        },
                    },
                },
            },
        }

        # Add autoscaling if specified
        if self.config.autoscaling and service_name in self.config.autoscaling:
            scaling_config = self.config.autoscaling[service_name]
            deployment["spec"]["replicas"] = scaling_config.get("min_replicas", 1)

        return deployment

    def _generate_service(
        self, service_name: str, service_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate Kubernetes Service manifest."""
        ports = []
        for port in service_config.get("ports", [8080]):
            ports.append(
                {
                    "port": port,
                    "targetPort": port,
                    "protocol": "TCP",
                }
            )

        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": service_name,
                "namespace": self.namespace,
                "labels": {
                    "app": service_name,
                    "lamina.environment": self.config.name,
                    "lamina.sigil": self.config.sigil,
                },
            },
            "spec": {
                "selector": {"app": service_name},
                "ports": ports,
                "type": service_config.get("service_type", "ClusterIP"),
            },
        }

        return service

    def _generate_configmap(self, service_name: str, config_data: dict[str, Any]) -> dict[str, Any]:
        """Generate Kubernetes ConfigMap manifest."""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{service_name}-config",
                "namespace": self.namespace,
                "labels": {
                    "app": service_name,
                    "lamina.environment": self.config.name,
                    "lamina.sigil": self.config.sigil,
                },
            },
            "data": {k: str(v) for k, v in config_data.items()},
        }

    def deploy_all_services(self) -> bool:
        """
        Deploy all services from environment configuration.

        Returns:
            True if all services deployed successfully
        """
        logger.info(f"{self.config.sigil} Starting full deployment to namespace: {self.namespace}")

        # Create namespace and setup RBAC
        if not self.create_namespace():
            return False

        if not self.setup_rbac():
            return False

        # Deploy each service
        success = True
        for service_name, service_config in self.config.services.items():
            if not self.deploy_service(service_name, service_config):
                success = False

        # Setup autoscaling if configured
        if success and self.config.autoscaling:
            success = self._setup_autoscaling()

        if success:
            logger.info(f"{self.config.sigil} Full deployment completed successfully")
        else:
            logger.error(f"{self.config.sigil} Deployment completed with errors")

        return success

    def _setup_autoscaling(self) -> bool:
        """Setup HorizontalPodAutoscaler for configured services."""
        logger.info(f"{self.config.sigil} Setting up autoscaling")

        success = True
        for service_name, scaling_config in self.config.autoscaling.items():
            hpa = {
                "apiVersion": "autoscaling/v2",
                "kind": "HorizontalPodAutoscaler",
                "metadata": {
                    "name": f"{service_name}-hpa",
                    "namespace": self.namespace,
                    "labels": {
                        "app": service_name,
                        "lamina.environment": self.config.name,
                        "lamina.sigil": self.config.sigil,
                    },
                },
                "spec": {
                    "scaleTargetRef": {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "name": service_name,
                    },
                    "minReplicas": scaling_config.get("min_replicas", 1),
                    "maxReplicas": scaling_config.get("max_replicas", 10),
                    "metrics": [
                        {
                            "type": "Resource",
                            "resource": {
                                "name": "cpu",
                                "target": {
                                    "type": "Utilization",
                                    "averageUtilization": scaling_config.get("target_cpu", 70),
                                },
                            },
                        }
                    ],
                },
            }

            with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
                yaml.dump(hpa, f)
                hpa_file = f.name

            try:
                self._run_kubectl(["apply", "-f", hpa_file])
                logger.info(f"{self.config.sigil} Autoscaling configured for {service_name}")
            except subprocess.CalledProcessError as e:
                logger.error(
                    f"{self.config.sigil} Failed to setup autoscaling for {service_name}: {e.stderr}"
                )
                success = False
            finally:
                Path(hpa_file).unlink(missing_ok=True)

        return success

    def get_deployment_status(self) -> dict[str, Any]:
        """
        Get status of all deployments in the namespace.

        Returns:
            Dictionary with deployment status information
        """
        try:
            result = self._run_kubectl(["get", "deployments", "-n", self.namespace, "-o", "json"])
            deployments = json.loads(result.stdout)

            status = {
                "namespace": self.namespace,
                "environment": self.config.name,
                "sigil": self.config.sigil,
                "deployments": [],
            }

            for deployment in deployments.get("items", []):
                name = deployment["metadata"]["name"]
                spec_replicas = deployment["spec"]["replicas"]
                status_replicas = deployment["status"].get("replicas", 0)
                ready_replicas = deployment["status"].get("readyReplicas", 0)

                status["deployments"].append(
                    {
                        "name": name,
                        "replicas": {
                            "desired": spec_replicas,
                            "current": status_replicas,
                            "ready": ready_replicas,
                        },
                        "ready": ready_replicas == spec_replicas,
                    }
                )

            return status

        except subprocess.CalledProcessError as e:
            logger.error(f"{self.config.sigil} Failed to get deployment status: {e.stderr}")
            return {"error": str(e.stderr)}

    def cleanup_deployment(self) -> bool:
        """
        Clean up all resources in the namespace.

        Returns:
            True if cleanup was successful
        """
        logger.info(f"{self.config.sigil} Cleaning up deployment in namespace: {self.namespace}")

        try:
            # Delete namespace (this removes all resources within it)
            self._run_kubectl(["delete", "namespace", self.namespace, "--ignore-not-found=true"])
            logger.info(f"{self.config.sigil} Namespace {self.namespace} deleted successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"{self.config.sigil} Failed to cleanup deployment: {e.stderr}")
            return False
