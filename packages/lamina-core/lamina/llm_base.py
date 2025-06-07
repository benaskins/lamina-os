# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Base LLM Client interface for Lamina
"""

from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def generate(
        self, prompt: str, temperature: float | None = None, max_tokens: int | None = None, **kwargs
    ) -> str:
        """Generate a response from the LLM."""
        pass

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float | None = None,
        max_tokens: int | None = None,
        **kwargs,
    ) -> str:
        """Chat completion with message history."""
        pass


def get_llm_client(provider: str = "lamina", **config) -> LLMClient:
    """Factory function to get an LLM client instance."""
    if provider == "lamina":
        from lamina.llm_client import LaminaLLMClient

        return LaminaLLMClient(config)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
