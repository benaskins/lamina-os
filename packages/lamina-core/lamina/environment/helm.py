# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Helm Chart Generator for GitOps Deployment

Generates production-ready Helm charts from environment configurations
for GitOps-driven Kubernetes deployments.
"""

import logging
import subprocess
from pathlib import Path

import yaml

from .config import EnvironmentConfig

logger = logging.getLogger(__name__)


class HelmError(Exception):
    """Raised when Helm operations fail."""

    pass


class HelmChartGenerator:
    """
    Generates Helm charts from environment configurations for GitOps deployment.

    Creates production-ready Helm charts with values files, templates, and
    CI/CD integration for automated deployment on merge to main.
    """

    def __init__(self, config: EnvironmentConfig, output_dir: Path):
        """
        Initialize Helm chart generator.

        Args:
            config: Environment configuration
            output_dir: Directory to output generated charts
        """
        if not config.is_production():
            raise ValueError("Helm chart generator only supports production environments")

        self.config = config
        self.output_dir = output_dir
        self.chart_name = f"lamina-{config.name}"
        self.chart_dir = output_dir / self.chart_name

        # Validate Helm availability
        self._validate_helm()

    def _validate_helm(self):
        """Validate Helm is available and functional."""
        try:
            result = subprocess.run(
                ["helm", "version", "--short"],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info(f"{self.config.sigil} Helm version: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise HelmError(f"Helm not available or not functional: {e}")

    def generate_chart(self) -> Path:
        """
        Generate complete Helm chart for the environment.

        Returns:
            Path to generated chart directory
        """
        logger.info(f"{self.config.sigil} Generating Helm chart: {self.chart_name}")

        # Create chart structure
        self._create_chart_structure()
        self._generate_chart_yaml()
        self._generate_values_yaml()
        self._generate_templates()
        self._generate_gitops_configs()

        logger.info(f"{self.config.sigil} Helm chart generated at: {self.chart_dir}")
        return self.chart_dir

    def _create_chart_structure(self):
        """Create standard Helm chart directory structure."""
        directories = [
            self.chart_dir,
            self.chart_dir / "templates",
            self.chart_dir / "charts",
            self.chart_dir / ".github" / "workflows",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _generate_chart_yaml(self):
        """Generate Chart.yaml metadata file."""
        chart_yaml = {
            "apiVersion": "v2",
            "name": self.chart_name,
            "description": f"Lamina OS {self.config.name} environment deployment",
            "version": "1.0.0",
            "appVersion": "1.0.0",
            "type": "application",
            "keywords": ["lamina", "ai", "agent", "breath-first"],
            "home": "https://github.com/benaskins/lamina-os",
            "sources": ["https://github.com/benaskins/lamina-os"],
            "maintainers": [
                {
                    "name": "Lamina High Council",
                    "email": "council@getlamina.ai",
                },
                {
                    "name": "Ben Askins",
                    "email": "human@getlamina.ai",
                },
            ],
            "annotations": {
                "lamina.environment": self.config.name,
                "lamina.sigil": self.config.sigil,
                "lamina.type": self.config.type,
            },
        }

        chart_file = self.chart_dir / "Chart.yaml"
        with open(chart_file, "w") as f:
            yaml.dump(chart_yaml, f, default_flow_style=False)

    def _generate_values_yaml(self):
        """Generate values.yaml with environment-specific defaults."""
        values = {
            "global": {
                "environment": self.config.name,
                "sigil": self.config.sigil,
                "namespace": f"lamina-{self.config.name}",
                "labels": {
                    "lamina.environment": self.config.name,
                    "lamina.sigil": self.config.sigil,
                    "app.kubernetes.io/part-of": "lamina-constellation",
                },
            },
            "namespace": {
                "create": True,
                "name": f"lamina-{self.config.name}",
                "labels": {
                    "lamina.environment": self.config.name,
                    "lamina.sigil": self.config.sigil,
                },
            },
            "serviceAccount": {
                "create": True,
                "name": "lamina-service-account",
                "annotations": {},
            },
            "rbac": {
                "create": True,
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
            },
            "services": {},
            "autoscaling": {
                "enabled": self.config.supports_feature("auto_scaling"),
            },
            "monitoring": {
                "enabled": self.config.supports_feature("comprehensive_monitoring"),
                "prometheus": (
                    self.config.monitoring.get("prometheus", {}) if self.config.monitoring else {}
                ),
                "grafana": (
                    self.config.monitoring.get("grafana", {}) if self.config.monitoring else {}
                ),
            },
            "security": {
                "networkPolicies": {
                    "enabled": self.config.security.get("network_policies", False),
                },
                "podSecurityPolicy": {
                    "enabled": True,
                },
                "mtls": {
                    "enabled": self.config.security.get("mtls", False),
                },
            },
            "resources": self.config.get_resource_limits(),
        }

        # Add service configurations
        for service_name, service_config in self.config.services.items():
            values["services"][service_name] = {
                "enabled": True,
                "image": {
                    "repository": service_config.get("image", service_name).split(":")[0],
                    "tag": service_config.get("image", service_name).split(":")[-1],
                    "pullPolicy": "IfNotPresent",
                },
                "replicaCount": service_config.get("replicas", 1),
                "service": {
                    "type": service_config.get("service_type", "ClusterIP"),
                    "ports": service_config.get("ports", [8080]),
                },
                "resources": service_config.get(
                    "resources",
                    {
                        "requests": {"memory": "512Mi", "cpu": "250m"},
                        "limits": {"memory": "1Gi", "cpu": "500m"},
                    },
                ),
                "env": service_config.get("environment", {}),
                "config": service_config.get("config", {}),
            }

        # Add autoscaling configurations
        if self.config.autoscaling:
            values["autoscaling"]["configs"] = {}
            for service_name, scaling_config in self.config.autoscaling.items():
                values["autoscaling"]["configs"][service_name] = {
                    "enabled": True,
                    "minReplicas": scaling_config.get("min_replicas", 1),
                    "maxReplicas": scaling_config.get("max_replicas", 10),
                    "targetCPUUtilizationPercentage": scaling_config.get("target_cpu", 70),
                }

        values_file = self.chart_dir / "values.yaml"
        with open(values_file, "w") as f:
            yaml.dump(values, f, default_flow_style=False)

    def _generate_templates(self):
        """Generate Helm template files."""
        templates_dir = self.chart_dir / "templates"

        # Generate core template files
        self._generate_namespace_template(templates_dir)
        self._generate_serviceaccount_template(templates_dir)
        self._generate_rbac_template(templates_dir)
        self._generate_service_templates(templates_dir)
        self._generate_deployment_templates(templates_dir)
        self._generate_configmap_templates(templates_dir)
        self._generate_hpa_templates(templates_dir)
        self._generate_network_policy_template(templates_dir)

    def _generate_namespace_template(self, templates_dir: Path):
        """Generate namespace template."""
        template = """{{- if .Values.namespace.create }}
apiVersion: v1
kind: Namespace
metadata:
  name: {{ .Values.namespace.name }}
  labels:
    {{- include "lamina.labels" . | nindent 4 }}
    {{- with .Values.namespace.labels }}
    {{- toYaml . | nindent 4 }}
    {{- end }}
  annotations:
    lamina.description: "{{ .Chart.Description }}"
    lamina.managed-by: "helm"
    lamina.chart: "{{ .Chart.Name }}-{{ .Chart.Version }}"
{{- end }}
"""
        (templates_dir / "namespace.yaml").write_text(template)

    def _generate_serviceaccount_template(self, templates_dir: Path):
        """Generate service account template."""
        template = """{{- if .Values.serviceAccount.create }}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ .Values.serviceAccount.name }}
  namespace: {{ .Values.namespace.name }}
  labels:
    {{- include "lamina.labels" . | nindent 4 }}
  {{- with .Values.serviceAccount.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
{{- end }}
"""
        (templates_dir / "serviceaccount.yaml").write_text(template)

    def _generate_rbac_template(self, templates_dir: Path):
        """Generate RBAC templates."""
        template = """{{- if .Values.rbac.create }}
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: {{ include "lamina.fullname" . }}-role
  namespace: {{ .Values.namespace.name }}
  labels:
    {{- include "lamina.labels" . | nindent 4 }}
rules:
{{- with .Values.rbac.rules }}
{{- toYaml . | nindent 0 }}
{{- end }}
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: {{ include "lamina.fullname" . }}-rolebinding
  namespace: {{ .Values.namespace.name }}
  labels:
    {{- include "lamina.labels" . | nindent 4 }}
subjects:
- kind: ServiceAccount
  name: {{ .Values.serviceAccount.name }}
  namespace: {{ .Values.namespace.name }}
roleRef:
  kind: Role
  name: {{ include "lamina.fullname" . }}-role
  apiGroup: rbac.authorization.k8s.io
{{- end }}
"""
        (templates_dir / "rbac.yaml").write_text(template)

    def _generate_service_templates(self, templates_dir: Path):
        """Generate service templates for each service."""
        for service_name in self.config.services.keys():
            template = f"""{{{{- if .Values.services.{service_name}.enabled }}}}
apiVersion: v1
kind: Service
metadata:
  name: {service_name}
  namespace: {{{{ .Values.namespace.name }}}}
  labels:
    {{{{- include "lamina.labels" . | nindent 4 }}}}
    app.kubernetes.io/component: {service_name}
spec:
  type: {{{{ .Values.services.{service_name}.service.type }}}}
  ports:
  {{{{- range .Values.services.{service_name}.service.ports }}}}
  - port: {{{{ . }}}}
    targetPort: {{{{ . }}}}
    protocol: TCP
  {{{{- end }}}}
  selector:
    {{{{- include "lamina.selectorLabels" . | nindent 4 }}}}
    app.kubernetes.io/component: {service_name}
{{{{- end }}}}
"""
            (templates_dir / f"{service_name}-service.yaml").write_text(template)

    def _generate_deployment_templates(self, templates_dir: Path):
        """Generate deployment templates for each service."""
        for service_name in self.config.services.keys():
            template = f"""{{{{- if .Values.services.{service_name}.enabled }}}}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service_name}
  namespace: {{{{ .Values.namespace.name }}}}
  labels:
    {{{{- include "lamina.labels" . | nindent 4 }}}}
    app.kubernetes.io/component: {service_name}
spec:
  replicas: {{{{ .Values.services.{service_name}.replicaCount }}}}
  selector:
    matchLabels:
      {{{{- include "lamina.selectorLabels" . | nindent 6 }}}}
      app.kubernetes.io/component: {service_name}
  template:
    metadata:
      labels:
        {{{{- include "lamina.selectorLabels" . | nindent 8 }}}}
        app.kubernetes.io/component: {service_name}
        lamina.environment: {{{{ .Values.global.environment }}}}
        lamina.sigil: {{{{ .Values.global.sigil }}}}
    spec:
      serviceAccountName: {{{{ .Values.serviceAccount.name }}}}
      securityContext:
        fsGroup: 1000
        runAsUser: 1000
        runAsGroup: 1000
      containers:
      - name: {service_name}
        image: "{{{{ .Values.services.{service_name}.image.repository }}}}:{{{{ .Values.services.{service_name}.image.tag }}}}"
        imagePullPolicy: {{{{ .Values.services.{service_name}.image.pullPolicy }}}}
        ports:
        {{{{- range .Values.services.{service_name}.service.ports }}}}
        - containerPort: {{{{ . }}}}
        {{{{- end }}}}
        env:
        - name: LAMINA_ENVIRONMENT
          value: {{{{ .Values.global.environment | quote }}}}
        - name: LAMINA_SIGIL
          value: {{{{ .Values.global.sigil | quote }}}}
        - name: LAMINA_NAMESPACE
          value: {{{{ .Values.namespace.name | quote }}}}
        {{{{- range $key, $value := .Values.services.{service_name}.env }}}}
        - name: {{{{ $key }}}}
          value: {{{{ $value | quote }}}}
        {{{{- end }}}}
        {{{{- if .Values.services.{service_name}.config }}}}
        envFrom:
        - configMapRef:
            name: {service_name}-config
        {{{{- end }}}}
        resources:
          {{{{- toYaml .Values.services.{service_name}.resources | nindent 10 }}}}
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
{{{{- end }}}}
"""
            (templates_dir / f"{service_name}-deployment.yaml").write_text(template)

    def _generate_configmap_templates(self, templates_dir: Path):
        """Generate ConfigMap templates for services with configuration."""
        for service_name, service_config in self.config.services.items():
            if "config" in service_config:
                template = f"""{{{{- if and .Values.services.{service_name}.enabled .Values.services.{service_name}.config }}}}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {service_name}-config
  namespace: {{{{ .Values.namespace.name }}}}
  labels:
    {{{{- include "lamina.labels" . | nindent 4 }}}}
    app.kubernetes.io/component: {service_name}
data:
  {{{{- range $key, $value := .Values.services.{service_name}.config }}}}
  {{{{ $key }}}}: {{{{ $value | quote }}}}
  {{{{- end }}}}
{{{{- end }}}}
"""
                (templates_dir / f"{service_name}-configmap.yaml").write_text(template)

    def _generate_hpa_templates(self, templates_dir: Path):
        """Generate HorizontalPodAutoscaler templates."""
        template = """{{- if .Values.autoscaling.enabled }}
{{- range $serviceName, $config := .Values.autoscaling.configs }}
{{- if $config.enabled }}
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ $serviceName }}-hpa
  namespace: {{ $.Values.namespace.name }}
  labels:
    {{- include "lamina.labels" $ | nindent 4 }}
    app.kubernetes.io/component: {{ $serviceName }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ $serviceName }}
  minReplicas: {{ $config.minReplicas }}
  maxReplicas: {{ $config.maxReplicas }}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {{ $config.targetCPUUtilizationPercentage }}
{{- end }}
{{- end }}
{{- end }}
"""
        (templates_dir / "hpa.yaml").write_text(template)

    def _generate_network_policy_template(self, templates_dir: Path):
        """Generate NetworkPolicy template."""
        template = """{{- if .Values.security.networkPolicies.enabled }}
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: {{ include "lamina.fullname" . }}-network-policy
  namespace: {{ .Values.namespace.name }}
  labels:
    {{- include "lamina.labels" . | nindent 4 }}
spec:
  podSelector:
    matchLabels:
      {{- include "lamina.selectorLabels" . | nindent 6 }}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: {{ .Values.namespace.name }}
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: {{ .Values.namespace.name }}
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
{{- end }}
"""
        (templates_dir / "networkpolicy.yaml").write_text(template)

    def _generate_gitops_configs(self):
        """Generate GitOps configuration files."""
        self._generate_helpers_template()
        self._generate_github_workflow()
        self._generate_argocd_application()

    def _generate_helpers_template(self):
        """Generate _helpers.tpl template file."""
        helpers = """{{/*
Expand the name of the chart.
*/}}
{{- define "lamina.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "lamina.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "lamina.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "lamina.labels" -}}
helm.sh/chart: {{ include "lamina.chart" . }}
{{ include "lamina.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
lamina.environment: {{ .Values.global.environment }}
lamina.sigil: {{ .Values.global.sigil }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "lamina.selectorLabels" -}}
app.kubernetes.io/name: {{ include "lamina.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
"""
        (self.chart_dir / "templates" / "_helpers.tpl").write_text(helpers)

    def _generate_github_workflow(self):
        """Generate GitHub Actions workflow for GitOps deployment."""
        workflow = f"""name: Deploy {self.config.name.title()} Environment

on:
  push:
    branches: [ main ]
    paths:
      - 'charts/{self.chart_name}/**'
      - 'environments/{self.config.name}/**'
  pull_request:
    branches: [ main ]
    paths:
      - 'charts/{self.chart_name}/**'
      - 'environments/{self.config.name}/**'

env:
  CHART_PATH: charts/{self.chart_name}
  ENVIRONMENT: {self.config.name}
  SIGIL: {self.config.sigil}

jobs:
  validate:
    name: {self.config.sigil} Validate Helm Chart
    runs-on: ubuntu-latest
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup Helm
      uses: azure/setup-helm@v4
      with:
        version: '3.14.0'

    - name: Lint Helm chart
      run: |
        helm lint ${{{{ env.CHART_PATH }}}}

    - name: Validate Helm templates
      run: |
        helm template lamina-{self.config.name} ${{{{ env.CHART_PATH }}}} --dry-run

  deploy:
    name: {self.config.sigil} Deploy to {self.config.name.title()}
    runs-on: ubuntu-latest
    needs: validate
    if: github.ref == 'refs/heads/main'
    environment: {self.config.name}
    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup Helm
      uses: azure/setup-helm@v4
      with:
        version: '3.14.0'

    - name: Configure kubectl
      run: |
        mkdir -p ${{{{ runner.temp }}}}/.kube
        echo "${{{{ secrets.KUBECONFIG }}}}" | base64 -d > ${{{{ runner.temp }}}}/.kube/config
        export KUBECONFIG=${{{{ runner.temp }}}}/.kube/config
        kubectl cluster-info

    - name: Deploy with Helm
      run: |
        export KUBECONFIG=${{{{ runner.temp }}}}/.kube/config
        helm upgrade --install lamina-{self.config.name} ${{{{ env.CHART_PATH }} \\
          --namespace lamina-{self.config.name} \\
          --create-namespace \\
          --wait \\
          --timeout 10m \\
          --set global.image.tag=${{{{ github.sha }}}} \\
          --set global.environment={self.config.name} \\
          --set global.sigil="{self.config.sigil}"

    - name: Verify deployment
      run: |
        export KUBECONFIG=${{{{ runner.temp }}}}/.kube/config
        kubectl get pods -n lamina-{self.config.name}
        kubectl get services -n lamina-{self.config.name}

    - name: Post-deployment status
      run: |
        echo "{self.config.sigil} Deployment to {self.config.name} completed successfully"
"""

        workflow_dir = self.chart_dir / ".github" / "workflows"
        (workflow_dir / f"deploy-{self.config.name}.yml").write_text(workflow)

    def _generate_argocd_application(self):
        """Generate ArgoCD Application manifest for GitOps."""
        argocd_app = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": {
                "name": f"lamina-{self.config.name}",
                "namespace": "argocd",
                "labels": {
                    "lamina.environment": self.config.name,
                    "lamina.sigil": self.config.sigil,
                },
                "finalizers": ["resources-finalizer.argocd.argoproj.io"],
            },
            "spec": {
                "project": "default",
                "source": {
                    "repoURL": "https://github.com/benaskins/lamina-os",
                    "targetRevision": "main",
                    "path": f"charts/{self.chart_name}",
                    "helm": {
                        "valueFiles": ["values.yaml"],
                        "parameters": [
                            {"name": "global.environment", "value": self.config.name},
                            {"name": "global.sigil", "value": self.config.sigil},
                        ],
                    },
                },
                "destination": {
                    "server": "https://kubernetes.default.svc",
                    "namespace": f"lamina-{self.config.name}",
                },
                "syncPolicy": {
                    "automated": {
                        "prune": True,
                        "selfHeal": True,
                        "allowEmpty": False,
                    },
                    "syncOptions": [
                        "CreateNamespace=true",
                        "PrunePropagationPolicy=foreground",
                        "PruneLast=true",
                    ],
                    "retry": {
                        "limit": 5,
                        "backoff": {
                            "duration": "5s",
                            "factor": 2,
                            "maxDuration": "3m",
                        },
                    },
                },
            },
        }

        argocd_file = self.chart_dir / "argocd-application.yaml"
        with open(argocd_file, "w") as f:
            yaml.dump(argocd_app, f, default_flow_style=False)

    def package_chart(self) -> Path:
        """
        Package the Helm chart into a .tgz file.

        Returns:
            Path to packaged chart
        """
        logger.info(f"{self.config.sigil} Packaging Helm chart: {self.chart_name}")

        try:
            result = subprocess.run(
                ["helm", "package", str(self.chart_dir), "--destination", str(self.output_dir)],
                capture_output=True,
                text=True,
                check=True,
            )

            # Extract package name from helm output
            package_line = [
                line for line in result.stdout.split("\n") if "Successfully packaged chart" in line
            ][0]
            package_path = Path(package_line.split(":")[-1].strip())

            logger.info(f"{self.config.sigil} Chart packaged successfully: {package_path}")
            return package_path

        except subprocess.CalledProcessError as e:
            raise HelmError(f"Failed to package chart: {e.stderr}")

    def validate_chart(self) -> bool:
        """
        Validate the generated Helm chart.

        Returns:
            True if chart is valid
        """
        logger.info(f"{self.config.sigil} Validating Helm chart: {self.chart_name}")

        try:
            # Lint the chart
            subprocess.run(
                ["helm", "lint", str(self.chart_dir)],
                capture_output=True,
                text=True,
                check=True,
            )

            # Dry-run template rendering
            subprocess.run(
                ["helm", "template", "test-release", str(self.chart_dir), "--dry-run"],
                capture_output=True,
                text=True,
                check=True,
            )

            logger.info(f"{self.config.sigil} Chart validation passed")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"{self.config.sigil} Chart validation failed: {e.stderr}")
            return False
