# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Build Manager for Lamina Infrastructure

This module manages timestamped/hashed build directories to ensure each build
can be uniquely identified and preserved.
"""

import hashlib
import json
import logging
import shutil
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class BuildManager:
    """Manages timestamped/hashed build directories"""

    def __init__(self, base_build_dir: str = ".build"):
        self.base_build_dir = Path(base_build_dir)
        self.builds_dir = self.base_build_dir / "builds"
        self.current_link = self.base_build_dir / "current"

        # Ensure build directories exist
        self.builds_dir.mkdir(parents=True, exist_ok=True)

    def generate_build_id(self, agent_name: str, build_inputs: dict) -> str:
        """Generate a unique build ID based on timestamp and content hash"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create content hash from build inputs
        content_str = json.dumps(build_inputs, sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()[:8]

        return f"{timestamp}_{agent_name}_{content_hash}"

    def create_build_directory(self, build_id: str) -> Path:
        """Create a new build directory with the given ID"""
        build_dir = self.builds_dir / build_id
        build_dir.mkdir(parents=True, exist_ok=True)

        # Create infrastructure subdirectory
        infra_dir = build_dir / "infrastructure"
        infra_dir.mkdir(exist_ok=True)

        logger.info(f"Created build directory: {build_dir}")
        return build_dir

    def get_build_info_path(self, build_id: str) -> Path:
        """Get the path to the build info file"""
        return self.builds_dir / build_id / "build_info.json"

    def save_build_info(self, build_id: str, build_info: dict) -> None:
        """Save build information to the build directory"""
        info_path = self.get_build_info_path(build_id)

        # Add metadata
        build_info.update(
            {
                "build_id": build_id,
                "created_at": datetime.now().isoformat(),
                "build_dir": str(self.builds_dir / build_id),
            }
        )

        with open(info_path, "w") as f:
            json.dump(build_info, f, indent=2)

        logger.info(f"Saved build info: {info_path}")

    def load_build_info(self, build_id: str) -> dict | None:
        """Load build information from the build directory"""
        info_path = self.get_build_info_path(build_id)

        if not info_path.exists():
            return None

        try:
            with open(info_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load build info from {info_path}: {e}")
            return None

    def update_current_symlink(self, build_id: str) -> None:
        """Update the 'current' symlink to point to the latest build"""
        build_dir = self.builds_dir / build_id

        if not build_dir.exists():
            logger.error(f"Build directory does not exist: {build_dir}")
            return

        # Remove existing symlink if it exists
        if self.current_link.exists() or self.current_link.is_symlink():
            self.current_link.unlink()

        # Create new symlink (use relative path)
        try:
            relative_path = build_dir.relative_to(self.base_build_dir)
            self.current_link.symlink_to(relative_path, target_is_directory=True)
            logger.info(f"Updated current symlink to: {build_dir}")
        except Exception as e:
            logger.error(f"Failed to create symlink: {e}")

    def list_builds(self) -> list[tuple[str, dict]]:
        """List all builds with their information"""
        builds = []

        for build_dir in self.builds_dir.iterdir():
            if build_dir.is_dir():
                build_info = self.load_build_info(build_dir.name)
                if build_info:
                    builds.append((build_dir.name, build_info))

        # Sort by creation time (newest first)
        builds.sort(key=lambda x: x[1].get("created_at", ""), reverse=True)
        return builds

    def get_current_build_id(self) -> str | None:
        """Get the current build ID from the symlink"""
        if not self.current_link.exists():
            return None

        try:
            target = self.current_link.resolve()
            return target.name
        except Exception as e:
            logger.error(f"Failed to resolve current symlink: {e}")
            return None

    def cleanup_old_builds(self, keep_count: int = 10) -> list[str]:
        """Clean up old builds, keeping only the specified number"""
        builds = self.list_builds()

        if len(builds) <= keep_count:
            return []

        # Get current build to avoid deleting it
        current_build_id = self.get_current_build_id()

        removed_builds = []
        builds_to_remove = builds[keep_count:]

        for build_id, _build_info in builds_to_remove:
            # Don't remove the current build
            if build_id == current_build_id:
                continue

            build_dir = self.builds_dir / build_id
            try:
                shutil.rmtree(build_dir)
                removed_builds.append(build_id)
                logger.info(f"Removed old build: {build_id}")
            except Exception as e:
                logger.error(f"Failed to remove build {build_id}: {e}")

        return removed_builds

    def get_infrastructure_dir(self, build_id: str | None = None) -> Path:
        """Get the infrastructure directory for a specific build or current build"""
        if build_id is None:
            if self.current_link.exists():
                return self.current_link / "infrastructure"
            else:
                # Fallback to legacy location
                return self.base_build_dir / "infrastructure"
        else:
            return self.builds_dir / build_id / "infrastructure"

    def copy_to_legacy_location(self, build_id: str) -> None:
        """Copy build artifacts to legacy .build/infrastructure location for compatibility"""
        source_dir = self.get_infrastructure_dir(build_id)
        legacy_dir = self.base_build_dir / "infrastructure"

        if not source_dir.exists():
            logger.warning(f"Source infrastructure directory does not exist: {source_dir}")
            return

        try:
            # Remove existing legacy directory
            if legacy_dir.exists():
                shutil.rmtree(legacy_dir)

            # Copy new build to legacy location
            shutil.copytree(source_dir, legacy_dir)
            logger.info(f"Copied build {build_id} to legacy location: {legacy_dir}")
        except Exception as e:
            logger.error(f"Failed to copy to legacy location: {e}")


def get_build_manager() -> BuildManager:
    """Get a singleton build manager instance"""
    return BuildManager()
