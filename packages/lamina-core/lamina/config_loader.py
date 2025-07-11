# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

import os
from pathlib import Path

import yaml


def _validate_path_safe(path: Path, allowed_base: Path) -> bool:
    """
    Validate that a path is safe and within allowed directory.

    Args:
        path: Path to validate
        allowed_base: Base directory that path must be within

    Returns:
        True if path is safe, False otherwise
    """
    try:
        # Resolve to absolute paths to handle symlinks and relative paths
        resolved_path = path.resolve()
        resolved_base = allowed_base.resolve()

        # Check if the resolved path is within the allowed base
        return resolved_path.is_relative_to(resolved_base)
    except (OSError, ValueError):
        return False


def _sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal.

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename

    Raises:
        ValueError: If filename contains invalid characters
    """
    # Remove path separators and other dangerous characters
    if ".." in filename or "/" in filename or "\\" in filename:
        raise ValueError(f"Invalid filename: {filename}")

    # Allow only alphanumeric, hyphens, underscores, and dots
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
    if not all(c in allowed_chars for c in filename):
        raise ValueError(f"Filename contains invalid characters: {filename}")

    return filename


def load_config(agent_name, config_file="known_entities.yaml"):
    """
    Load configuration for an agent, checking test directory first.

    Args:
        agent_name (str): Name of the agent
        config_file (str): Name of the configuration file

    Returns:
        dict: Configuration data

    Raises:
        FileNotFoundError: If the configuration file doesn't exist
        ValueError: If agent_name or config_file contains invalid characters
    """
    # Sanitize inputs to prevent path traversal
    try:
        agent_name = _sanitize_filename(agent_name)
        config_file = _sanitize_filename(config_file)
    except ValueError as e:
        raise ValueError(f"Invalid input: {e}")

    # First check in lamina/tests/agents for test agents
    lamina_dir = os.path.dirname(os.path.dirname(__file__))
    test_base_path = Path(lamina_dir) / "tests" / "agents"
    test_config_path = test_base_path / agent_name / config_file

    # Validate test path is safe
    if test_config_path.exists() and _validate_path_safe(test_config_path, test_base_path):
        with open(test_config_path) as file:
            return yaml.safe_load(file)

    # If not found in test directory, check sanctuary
    sanctuary_dir = os.getenv("SANCTUARY_DIR")
    if not sanctuary_dir:
        # Default to ../sanctuary relative to this file
        sanctuary_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sanctuary"))

    # Convert to Path object for easier manipulation
    sanctuary_path = Path(sanctuary_dir)
    agent_config_path = sanctuary_path / "agents" / agent_name / config_file

    # Validate sanctuary path is safe
    if not _validate_path_safe(agent_config_path, sanctuary_path):
        raise ValueError(f"Path traversal detected: {agent_config_path}")

    # Debug output
    print(f"DEBUG: SANCTUARY_DIR={sanctuary_dir}")
    print(f"DEBUG: agent_config_path={agent_config_path}")

    if not agent_config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {agent_config_path}")

    with open(agent_config_path) as file:
        return yaml.safe_load(file)
