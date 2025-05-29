# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Infrastructure Template Engine for Lamina

This module processes infrastructure templates using agent-specific values
from sanctuary configurations to generate customized infrastructure files.
"""

import logging
import os
import re
from pathlib import Path
from typing import Any

from lamina.build_manager import get_build_manager
from lamina.infrastructure_values import get_infrastructure_values

logger = logging.getLogger(__name__)


class InfrastructureTemplateEngine:
    """Template engine for processing infrastructure templates"""

    def __init__(
        self,
        templates_dir: str | None = None,
        output_dir: str | None = None,
        build_id: str | None = None,
    ):
        self.templates_dir = Path(templates_dir or "lamina/infrastructure")
        self.build_manager = get_build_manager()
        self.build_id = build_id

        if output_dir:
            self.output_dir = Path(output_dir)
        elif build_id:
            self.output_dir = self.build_manager.get_infrastructure_dir(build_id)
        else:
            # Use current build or fallback to legacy location
            self.output_dir = self.build_manager.get_infrastructure_dir()

    def render_template(self, template_content: str, values: dict[str, Any]) -> str:
        """Render a template string with the provided values"""

        def replace_variable(match):
            var_path = match.group(1)
            keys = var_path.split(".")
            value = values

            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    logger.warning(f"Template variable '{var_path}' not found in values")
                    return match.group(0)  # Return original if not found

            return str(value)

        # Replace {{variable.path}} with actual values, but skip {{ word }} patterns (single words)
        # This preserves Vector's template syntax like {{ job }} while processing our {{agent.name}} syntax
        pattern = r"\{\{([^}]+\.[^}]+)\}\}"  # Only match patterns with dots (our syntax)
        result = re.sub(pattern, replace_variable, template_content)

        # Also handle simple variable names without dots if they match our values
        simple_pattern = r"\{\{(agent|container|nginx|ollama|grafana|vector|volumes)\}\}"
        return re.sub(simple_pattern, replace_variable, result)

    def process_template_file(self, template_path: Path, agent_name: str) -> str:
        """Process a single template file and return the rendered content"""
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        # Load infrastructure values for the agent
        infra_values = get_infrastructure_values(agent_name)
        values_dict = infra_values.to_dict()

        # Read template content
        with open(template_path) as f:
            template_content = f.read()

        # Render the template
        return self.render_template(template_content, values_dict)

    def generate_infrastructure_files(self, agent_name: str, force: bool = False) -> dict[str, str]:
        """Generate all infrastructure files for an agent"""
        generated_files = {}

        # Define template mappings
        template_mappings = {
            "docker-compose.yml.template": "docker-compose.yml",
            "docker-compose-unified.yml.template": "docker-compose-unified.yml",
            "nginx/nginx.conf.template": "nginx/nginx.conf",
            "nginx/nginx-unified.conf.template": "nginx/nginx-unified.conf",
            "vector/vector.toml.template": "vector/vector.toml",
            "docker/ollama/Dockerfile.template": "docker/ollama/Dockerfile",
            "docker/ollama/entrypoint.sh.template": "docker/ollama/entrypoint.sh",
        }

        # Define static files to copy (no templating needed)
        static_files = [
            "docker-compose.override.yml",
            "nginx/Dockerfile",
            "vector/Dockerfile",
            "docker/chromadb/",
            "loki/",
            "grafana/",
        ]

        for template_file, output_file in template_mappings.items():
            template_path = self.templates_dir / template_file
            output_path = self.output_dir / output_file

            if not template_path.exists():
                logger.warning(f"Template not found: {template_path}")
                continue

            try:
                # Process the template
                rendered_content = self.process_template_file(template_path, agent_name)

                # Create output directory if it doesn't exist
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # Check if file exists and force flag
                if output_path.exists() and not force:
                    logger.info(
                        f"Skipping existing file: {output_path} (use force=True to overwrite)"
                    )
                    continue

                # Write the rendered content
                with open(output_path, "w") as f:
                    f.write(rendered_content)

                # Make shell scripts executable
                if output_file.endswith(".sh"):
                    os.chmod(output_path, 0o755)

                generated_files[output_file] = str(output_path)
                logger.info(f"Generated infrastructure file: {output_path}")

            except Exception as e:
                logger.error(f"Failed to process template {template_file}: {e}")
                continue

        # Copy static files
        import shutil

        for static_item in static_files:
            source_path = self.templates_dir / static_item
            target_path = self.output_dir / static_item

            if not source_path.exists():
                logger.warning(f"Static file/directory not found: {source_path}")
                continue

            try:
                # Create parent directory if needed
                target_path.parent.mkdir(parents=True, exist_ok=True)

                if source_path.is_dir():
                    # Copy directory recursively
                    if target_path.exists() and not force:
                        logger.info(f"Skipping existing directory: {target_path}")
                        continue
                    if target_path.exists():
                        shutil.rmtree(target_path)
                    shutil.copytree(source_path, target_path)
                    generated_files[f"{static_item}/"] = str(target_path)
                    logger.info(f"Copied static directory: {target_path}")
                else:
                    # Copy file
                    if target_path.exists() and not force:
                        logger.info(f"Skipping existing file: {target_path}")
                        continue
                    shutil.copy2(source_path, target_path)
                    generated_files[static_item] = str(target_path)
                    logger.info(f"Copied static file: {target_path}")

            except Exception as e:
                logger.error(f"Failed to copy static item {static_item}: {e}")
                continue

        # Copy agent-specific Modelfile for Ollama
        try:
            infra_values = get_infrastructure_values(agent_name)
            modelfile_path = infra_values.get("ollama.modelfile_path")
            if modelfile_path:
                source_modelfile = Path(modelfile_path)
                target_modelfile = self.output_dir / "docker" / "ollama" / "Modelfile"

                if source_modelfile.exists():
                    # Create directory if needed
                    target_modelfile.parent.mkdir(parents=True, exist_ok=True)

                    if target_modelfile.exists() and not force:
                        logger.info(f"Skipping existing Modelfile: {target_modelfile}")
                    else:
                        shutil.copy2(source_modelfile, target_modelfile)
                        generated_files["docker/ollama/Modelfile"] = str(target_modelfile)
                        logger.info(f"Copied Modelfile: {target_modelfile}")
                else:
                    logger.warning(f"Modelfile not found: {source_modelfile}")
        except Exception as e:
            logger.error(f"Failed to copy Modelfile: {e}")

        return generated_files

    def generate_docker_compose(self, agent_name: str, force: bool = False) -> str | None:
        """Generate docker-compose.yml for a specific agent"""
        template_path = self.templates_dir / "docker-compose.yml.template"
        output_path = self.output_dir / "docker-compose.yml"

        if not template_path.exists():
            logger.error(f"Docker compose template not found: {template_path}")
            return None

        if output_path.exists() and not force:
            logger.info(f"Docker compose file exists: {output_path} (use force=True to overwrite)")
            return str(output_path)

        try:
            rendered_content = self.process_template_file(template_path, agent_name)

            with open(output_path, "w") as f:
                f.write(rendered_content)

            logger.info(f"Generated docker-compose.yml for agent: {agent_name}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate docker-compose.yml: {e}")
            return None

    def generate_nginx_config(self, agent_name: str, force: bool = False) -> str | None:
        """Generate nginx configuration for a specific agent"""
        template_path = self.templates_dir / "nginx" / "nginx.conf.template"
        output_path = self.output_dir / "nginx" / "nginx.conf"

        if not template_path.exists():
            logger.error(f"Nginx template not found: {template_path}")
            return None

        if output_path.exists() and not force:
            logger.info(f"Nginx config exists: {output_path} (use force=True to overwrite)")
            return str(output_path)

        try:
            rendered_content = self.process_template_file(template_path, agent_name)

            # Create nginx directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w") as f:
                f.write(rendered_content)

            logger.info(f"Generated nginx.conf for agent: {agent_name}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate nginx.conf: {e}")
            return None

    def validate_agent_values(self, agent_name: str) -> bool:
        """Validate that an agent has all required infrastructure values"""
        try:
            infra_values = get_infrastructure_values(agent_name)

            # Check required values
            required_paths = [
                "agent.name",
                "nginx.upstream_name",
                "nginx.server_name",
                "nginx.ssl_client_cn",
                "ollama.model_name",
                "ollama.modelfile_path",
            ]

            for path in required_paths:
                value = infra_values.get(path)
                if value is None:
                    logger.error(
                        f"Missing required infrastructure value for agent {agent_name}: {path}"
                    )
                    return False

            logger.info(f"Infrastructure values validated for agent: {agent_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to validate infrastructure values for {agent_name}: {e}")
            return False


def get_template_engine(build_id: str | None = None) -> InfrastructureTemplateEngine:
    """Get a template engine instance"""
    return InfrastructureTemplateEngine(build_id=build_id)


def generate_infrastructure_for_agent(
    agent_name: str, force: bool = False, build_id: str | None = None
) -> dict[str, str]:
    """Generate all infrastructure files for an agent"""
    build_manager = get_build_manager()

    if build_id is None:
        # Generate new build ID
        from lamina.infrastructure_values import get_infrastructure_values

        infra_values = get_infrastructure_values(agent_name)
        build_inputs = {
            "agent_name": agent_name,
            "infrastructure_values": infra_values.to_dict(),
            "force": force,
        }
        build_id = build_manager.generate_build_id(agent_name, build_inputs)

        # Create build directory
        build_manager.create_build_directory(build_id)

        # Save build info
        build_info = {
            "agent_name": agent_name,
            "force": force,
            "infrastructure_values": infra_values.to_dict(),
        }
        build_manager.save_build_info(build_id, build_info)

        logger.info(f"Created new build: {build_id}")

    # Create engine with specific build ID
    engine = get_template_engine(build_id=build_id)
    generated_files = engine.generate_infrastructure_files(agent_name, force)

    if generated_files:
        # Update current symlink to point to this build
        build_manager.update_current_symlink(build_id)

        # Copy to legacy location for backward compatibility
        build_manager.copy_to_legacy_location(build_id)

        logger.info(f"Build {build_id} completed successfully")

    return generated_files


def generate_unified_infrastructure(
    force: bool = False, build_id: str | None = None
) -> dict[str, str]:
    """Generate unified infrastructure for multi-agent mode"""
    return generate_infrastructure_for_agent("multi-agent", force=force, build_id=build_id)


def validate_agent_infrastructure(agent_name: str) -> bool:
    """Validate that an agent has all required infrastructure values"""
    engine = get_template_engine()
    return engine.validate_agent_values(agent_name)
