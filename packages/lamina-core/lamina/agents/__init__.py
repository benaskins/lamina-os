# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Agent module for Lamina OS

This module provides the base Agent class and utilities for creating
presence-aware AI agents with essence-based configuration.
"""

from lamina.agents.base import Agent, AgentEssence
from lamina.agents.essence_parser import EssenceParser

__all__ = ["Agent", "AgentEssence", "EssenceParser"]
