# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Environment Management Module

Provides breath-aware environment configuration and management
for development, test, and production deployments.
"""

from .config import EnvironmentConfig, load_environment_config
from .manager import EnvironmentManager
from .validators import validate_environment_config

__all__ = [
    "EnvironmentConfig",
    "EnvironmentManager",
    "load_environment_config",
    "validate_environment_config",
]
