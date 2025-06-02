# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Lamina LLM Serve - Centralized model caching and serving layer

This package provides unified access to language models for Lamina OS,
handling model discovery, caching, and backend routing.
"""

__version__ = "0.2.0"

from .backends import get_backend_for_model
from .model_manager import ModelManager
from .server import LLMServer

__all__ = ["ModelManager", "get_backend_for_model", "LLMServer"]
