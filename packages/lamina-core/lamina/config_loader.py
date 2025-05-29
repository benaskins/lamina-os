# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

import os
from pathlib import Path

import yaml


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
    """
    # First check in lamina/tests/agents for test agents
    lamina_dir = os.path.dirname(os.path.dirname(__file__))
    test_config_path = Path(lamina_dir) / "tests" / "agents" / agent_name / config_file

    if test_config_path.exists():
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

    # Debug output
    print(f"DEBUG: SANCTUARY_DIR={sanctuary_dir}")
    print(f"DEBUG: agent_config_path={agent_config_path}")

    if not agent_config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {agent_config_path}")

    with open(agent_config_path) as file:
        return yaml.safe_load(file)
