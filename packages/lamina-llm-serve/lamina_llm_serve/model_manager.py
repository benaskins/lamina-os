# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Model Manager - Core model discovery and management

Handles loading model manifests, validating model availability,
and providing model metadata to the rest of the system.
"""

import logging
import os
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Central manager for all language models in Lamina OS.

    Provides unified access to model metadata, paths, and configurations
    while abstracting backend-specific details.
    """

    def __init__(self, manifest_path: str = "models.yaml", models_dir: str = "models"):
        self.manifest_path = Path(manifest_path)
        self.models_dir = Path(models_dir)
        self.manifest = {}
        self.models = {}
        self.backends = {}
        self.categories = {}
        self.defaults = {}

        self._load_manifest()

    def _load_manifest(self):
        """Load and parse the model manifest file"""
        try:
            if not self.manifest_path.exists():
                logger.warning(f"Model manifest not found at {self.manifest_path}")
                return

            with open(self.manifest_path) as f:
                self.manifest = yaml.safe_load(f)

            self.models = self.manifest.get("models", {})
            self.backends = self.manifest.get("backends", {})
            self.categories = self.manifest.get("categories", {})
            self.defaults = self.manifest.get("defaults", {})

            logger.info(f"Loaded {len(self.models)} models from manifest")

        except Exception as e:
            logger.error(f"Failed to load model manifest: {e}")
            raise

    def list_models(self) -> list[str]:
        """List all available model names"""
        return list(self.models.keys())

    def get_model_info(self, model_name: str) -> dict[str, Any] | None:
        """Get detailed information about a specific model"""
        return self.models.get(model_name)

    def get_model_path(self, model_name: str) -> str | None:
        """Get the filesystem path for a model"""
        model_info = self.get_model_info(model_name)
        if not model_info:
            return None
        return model_info.get("path")

    def get_model_backend(self, model_name: str) -> str | None:
        """Get the backend type for a model"""
        model_info = self.get_model_info(model_name)
        if not model_info:
            return None
        return model_info.get("backend")

    def get_backend_config(self, backend_name: str) -> dict[str, Any] | None:
        """Get configuration for a specific backend"""
        return self.backends.get(backend_name)

    def get_models_by_category(self, category: str) -> list[str]:
        """Get all models in a specific category"""
        return self.categories.get(category, [])

    def get_default_model(self, use_case: str) -> str | None:
        """Get the default model for a specific use case"""
        return self.defaults.get(use_case)

    def is_model_available(self, model_name: str) -> bool:
        """Check if a model is available on the filesystem"""
        model_path = self.get_model_path(model_name)
        if not model_path:
            return False

        # Convert relative paths to absolute
        if not os.path.isabs(model_path):
            model_path = self.models_dir / model_path

        return Path(model_path).exists()

    def validate_models(self) -> dict[str, bool]:
        """Validate availability of all models in manifest"""
        results = {}
        for model_name in self.list_models():
            results[model_name] = self.is_model_available(model_name)
        return results

    def get_missing_models(self) -> list[str]:
        """Get list of models that are in manifest but not on filesystem"""
        missing = []
        for model_name in self.list_models():
            if not self.is_model_available(model_name):
                missing.append(model_name)
        return missing

    def get_model_stats(self) -> dict[str, Any]:
        """Get statistics about the model collection"""
        validation = self.validate_models()
        available_count = sum(validation.values())
        total_count = len(validation)

        stats = {
            "total_models": total_count,
            "available_models": available_count,
            "missing_models": total_count - available_count,
            "categories": list(self.categories.keys()),
            "backends": list(self.backends.keys()),
            "use_cases": list(self.defaults.keys()),
        }

        return stats

    def suggest_model(self, requirements: dict[str, Any]) -> str | None:
        """
        Suggest the best model based on requirements.

        Args:
            requirements: Dict with keys like 'use_case', 'max_size', 'category'

        Returns:
            Name of suggested model or None
        """
        # Start with use case default if specified
        use_case = requirements.get("use_case")
        if use_case and use_case in self.defaults:
            suggested = self.defaults[use_case]
            if self.is_model_available(suggested):
                return suggested

        # Try category-based selection
        category = requirements.get("category")
        if category and category in self.categories:
            for model_name in self.categories[category]:
                if self.is_model_available(model_name):
                    return model_name

        # Fall back to first available model
        for model_name in self.list_models():
            if self.is_model_available(model_name):
                return model_name

        return None

    def reload_manifest(self):
        """Reload the model manifest from disk"""
        logger.info("Reloading model manifest")
        self._load_manifest()

    def get_model_for_agent(self, agent_config: dict[str, Any]) -> str | None:
        """
        Get the appropriate model for an agent configuration.

        Args:
            agent_config: Agent configuration with ai_model, use_case, etc.

        Returns:
            Model name or None
        """
        # Check if agent specifies exact model
        if "ai_model" in agent_config:
            requested_model = agent_config["ai_model"]
            if requested_model in self.models:
                return requested_model

        # Use agent template to determine use case
        template = agent_config.get("template", "conversational")
        use_case_map = {
            "conversational": "conversational",
            "analytical": "analytical",
            "security": "security",
            "reasoning": "reasoning",
        }

        use_case = use_case_map.get(template, "conversational")

        # Get model for use case
        requirements = {"use_case": use_case, "category": agent_config.get("category", "balanced")}

        return self.suggest_model(requirements)
