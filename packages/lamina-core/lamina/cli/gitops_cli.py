# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
GitOps CLI Commands

Provides CLI commands for GitOps-driven Kubernetes deployments using
Helm charts and automated CI/CD pipelines.
"""

import logging
from pathlib import Path

import click

from ..environment.config import load_environment_config, validate_environment_name
from ..environment.helm import HelmChartGenerator, HelmError

logger = logging.getLogger(__name__)


@click.group(name="gitops")
def gitops_cli():
    """GitOps commands for Kubernetes deployment management."""
    pass


@gitops_cli.command(name="generate-charts")
@click.argument("environment", type=str)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(path_type=Path),
    default=Path.cwd() / "charts",
    help="Output directory for generated charts",
)
@click.option(
    "--validate/--no-validate",
    default=True,
    help="Validate generated charts",
)
@click.option(
    "--package/--no-package",
    default=False,
    help="Package charts into .tgz files",
)
def generate_charts(environment: str, output_dir: Path, validate: bool, package: bool):
    """
    Generate Helm charts for GitOps deployment.

    Creates production-ready Helm charts with CI/CD integration for the
    specified environment. Charts include templates, values, and GitOps
    configuration for automated deployment on merge to main.

    ENVIRONMENT: Environment name (development, test, production)
    """
    if not validate_environment_name(environment):
        click.echo(f"❌ Invalid environment: {environment}")
        click.echo("Valid environments: development, test, production")
        return

    try:
        # Load environment configuration
        config = load_environment_config(environment)
        click.echo(f"{config.sigil} Loading configuration for {environment} environment")

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate Helm chart
        generator = HelmChartGenerator(config, output_dir)
        chart_dir = generator.generate_chart()

        click.echo(f"{config.sigil} Helm chart generated: {chart_dir}")

        # Validate chart if requested
        if validate:
            click.echo(f"{config.sigil} Validating generated chart...")
            if generator.validate_chart():
                click.echo(f"{config.sigil} ✅ Chart validation passed")
            else:
                click.echo(f"{config.sigil} ❌ Chart validation failed")
                return

        # Package chart if requested
        if package:
            click.echo(f"{config.sigil} Packaging chart...")
            package_path = generator.package_chart()
            click.echo(f"{config.sigil} ✅ Chart packaged: {package_path}")

        # Display next steps
        click.echo(f"\n{config.sigil} GitOps Setup Complete!")
        click.echo("\n📋 Next Steps:")
        click.echo("  1. Commit the generated chart to your repository:")
        click.echo(f"     git add {chart_dir}")
        click.echo(f"     git commit -m 'feat: add {environment} Helm chart for GitOps deployment'")
        click.echo("  2. Configure your CI/CD secrets:")
        click.echo("     - KUBECONFIG: Base64-encoded kubeconfig for your cluster")
        click.echo("  3. Push to main branch to trigger deployment:")
        click.echo("     git push origin main")
        click.echo("\n🚀 Future deployments will be automated on merge to main!")

    except FileNotFoundError as e:
        click.echo(f"❌ Environment configuration not found: {e}")
        click.echo(f"Run 'lamina environment create {environment}' first")
    except HelmError as e:
        click.echo(f"❌ Helm error: {e}")
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        logger.exception("Error generating charts")


@gitops_cli.command(name="deploy")
@click.argument("environment", type=str)
@click.option(
    "--chart-path",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to Helm chart (defaults to charts/lamina-{environment})",
)
@click.option(
    "--namespace",
    "-n",
    type=str,
    help="Kubernetes namespace (defaults to lamina-{environment})",
)
@click.option(
    "--dry-run/--no-dry-run",
    default=False,
    help="Perform a dry run without actually deploying",
)
@click.option(
    "--wait/--no-wait",
    default=True,
    help="Wait for deployment to complete",
)
@click.option(
    "--timeout",
    "-t",
    type=int,
    default=600,
    help="Timeout for deployment in seconds",
)
def deploy(
    environment: str,
    chart_path: Path | None,
    namespace: str | None,
    dry_run: bool,
    wait: bool,
    timeout: int,
):
    """
    Deploy environment using Helm chart.

    Deploys the specified environment to Kubernetes using the generated
    Helm chart. This command is typically used for manual deployments
    or testing before setting up full GitOps automation.

    ENVIRONMENT: Environment name (development, test, production)
    """
    if not validate_environment_name(environment):
        click.echo(f"❌ Invalid environment: {environment}")
        return

    try:
        # Load environment configuration
        config = load_environment_config(environment)

        # Set defaults
        if chart_path is None:
            chart_path = Path.cwd() / "charts" / f"lamina-{environment}"
        if namespace is None:
            namespace = f"lamina-{environment}"

        if not chart_path.exists():
            click.echo(f"❌ Chart not found: {chart_path}")
            click.echo(f"Run 'lamina gitops generate-charts {environment}' first")
            return

        click.echo(f"{config.sigil} Deploying {environment} environment")
        click.echo(f"📊 Chart: {chart_path}")
        click.echo(f"🎯 Namespace: {namespace}")

        # Build helm command
        cmd = [
            "helm",
            "upgrade",
            "--install",
            f"lamina-{environment}",
            str(chart_path),
            "--namespace",
            namespace,
            "--create-namespace",
        ]

        if dry_run:
            cmd.append("--dry-run")
            click.echo(f"{config.sigil} Performing dry run...")

        if wait and not dry_run:
            cmd.extend(["--wait", "--timeout", f"{timeout}s"])

        # Add environment-specific values
        cmd.extend(
            [
                "--set",
                f"global.environment={environment}",
                "--set",
                f"global.sigil={config.sigil}",
            ]
        )

        # Execute deployment
        import subprocess

        click.echo(f"{config.sigil} Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            click.echo(f"{config.sigil} ✅ Deployment successful!")
            if not dry_run:
                click.echo("\n📋 Deployment Status:")
                click.echo(result.stdout)
        else:
            click.echo(f"{config.sigil} ❌ Deployment failed!")
            click.echo(f"Error: {result.stderr}")

    except FileNotFoundError as e:
        click.echo(f"❌ Environment configuration not found: {e}")
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        logger.exception("Error during deployment")


@gitops_cli.command(name="status")
@click.argument("environment", type=str)
@click.option(
    "--namespace",
    "-n",
    type=str,
    help="Kubernetes namespace (defaults to lamina-{environment})",
)
def status(environment: str, namespace: str | None):
    """
    Check deployment status for environment.

    Shows the current status of deployments, services, and pods
    for the specified environment in Kubernetes.

    ENVIRONMENT: Environment name (development, test, production)
    """
    if not validate_environment_name(environment):
        click.echo(f"❌ Invalid environment: {environment}")
        return

    try:
        # Load environment configuration
        config = load_environment_config(environment)

        if namespace is None:
            namespace = f"lamina-{environment}"

        click.echo(f"{config.sigil} Checking status for {environment} environment")
        click.echo(f"🎯 Namespace: {namespace}")

        import subprocess

        # Check deployments
        click.echo("\n📊 Deployments:")
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "deployments",
                "-n",
                namespace,
                "--output=custom-columns=NAME:.metadata.name,READY:.status.readyReplicas,UP-TO-DATE:.status.updatedReplicas,AVAILABLE:.status.availableReplicas",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            click.echo(result.stdout)
        else:
            click.echo(f"❌ Failed to get deployments: {result.stderr}")

        # Check services
        click.echo("\n🌐 Services:")
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "services",
                "-n",
                namespace,
                "--output=custom-columns=NAME:.metadata.name,TYPE:.spec.type,CLUSTER-IP:.spec.clusterIP,PORTS:.spec.ports[*].port",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            click.echo(result.stdout)
        else:
            click.echo(f"❌ Failed to get services: {result.stderr}")

        # Check pods
        click.echo("\n🐳 Pods:")
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "pods",
                "-n",
                namespace,
                "--output=custom-columns=NAME:.metadata.name,STATUS:.status.phase,RESTARTS:.status.containerStatuses[0].restartCount,AGE:.metadata.creationTimestamp",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            click.echo(result.stdout)
        else:
            click.echo(f"❌ Failed to get pods: {result.stderr}")

    except FileNotFoundError as e:
        click.echo(f"❌ Environment configuration not found: {e}")
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        logger.exception("Error checking status")


@gitops_cli.command(name="setup")
@click.argument("environment", type=str)
@click.option(
    "--repo-url",
    type=str,
    default="https://github.com/benaskins/lamina-os",
    help="Git repository URL",
)
@click.option(
    "--argocd/--no-argocd",
    default=True,
    help="Generate ArgoCD Application manifest",
)
def setup(environment: str, repo_url: str, argocd: bool):
    """
    Complete GitOps setup for environment.

    Generates Helm charts, CI/CD workflows, and ArgoCD applications
    for a complete GitOps deployment setup. This is the all-in-one
    command for setting up production Kubernetes deployments.

    ENVIRONMENT: Environment name (development, test, production)
    """
    if not validate_environment_name(environment):
        click.echo(f"❌ Invalid environment: {environment}")
        return

    try:
        # Load environment configuration
        config = load_environment_config(environment)
        click.echo(f"{config.sigil} Setting up GitOps for {environment} environment")

        # Create charts directory
        charts_dir = Path.cwd() / "charts"
        charts_dir.mkdir(exist_ok=True)

        # Generate Helm chart
        click.echo(f"{config.sigil} Generating Helm chart...")
        generator = HelmChartGenerator(config, charts_dir)
        chart_dir = generator.generate_chart()

        # Validate chart
        click.echo(f"{config.sigil} Validating chart...")
        if not generator.validate_chart():
            click.echo(f"{config.sigil} ❌ Chart validation failed")
            return

        # Package chart
        click.echo(f"{config.sigil} Packaging chart...")
        package_path = generator.package_chart()

        click.echo(f"{config.sigil} ✅ GitOps setup complete!")
        click.echo("\n📋 Generated Files:")
        click.echo(f"  📊 Helm Chart: {chart_dir}")
        click.echo(f"  📦 Package: {package_path}")
        click.echo(f"  🔄 GitHub Workflow: {chart_dir}/.github/workflows/")
        if argocd:
            click.echo(f"  🐙 ArgoCD App: {chart_dir}/argocd-application.yaml")

        # Display comprehensive setup instructions
        click.echo("\n🚀 Complete GitOps Deployment Setup:")
        click.echo("\n1️⃣ Commit and Push Charts:")
        click.echo("   git add charts/")
        click.echo(f"   git commit -m 'feat: GitOps setup for {environment} environment'")
        click.echo("   git push origin main")

        click.echo("\n2️⃣ Configure Repository Secrets:")
        click.echo("   • KUBECONFIG: Base64-encoded kubeconfig")
        click.echo("   • Navigate to: Settings > Secrets and variables > Actions")

        click.echo("\n3️⃣ Deploy via GitOps:")
        click.echo("   • Automatic: Any changes to charts/ or environments/ trigger deployment")
        click.echo("   • Manual: Push to main branch or run GitHub Actions workflow")

        if argocd:
            click.echo("\n4️⃣ ArgoCD Setup (Optional):")
            click.echo(f"   kubectl apply -f {chart_dir}/argocd-application.yaml")
            click.echo("   # Enables continuous deployment from main branch")

        click.echo("\n✨ Future deployments will be fully automated!")
        click.echo("   Just modify charts or environment configs and merge to main.")

    except FileNotFoundError as e:
        click.echo(f"❌ Environment configuration not found: {e}")
        click.echo(f"Run 'lamina environment create {environment}' first")
    except HelmError as e:
        click.echo(f"❌ Helm error: {e}")
    except Exception as e:
        click.echo(f"❌ Unexpected error: {e}")
        logger.exception("Error during GitOps setup")
