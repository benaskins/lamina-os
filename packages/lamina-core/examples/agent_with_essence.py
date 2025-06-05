#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2025 Ben Askins

"""
Example: Creating a Lamina Agent with Essence Configuration

This example demonstrates how to create a custom agent that inherits from
the base Agent class and uses an essence markdown file for configuration.
"""

import asyncio
import logging
from pathlib import Path

from lamina.agents import Agent, AgentEssence
from lamina.llm_client import get_llm_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PoetAgent(Agent):
    """
    A poetry-focused agent that demonstrates essence-based configuration.
    
    This agent specializes in creative, poetic responses while maintaining
    the breath-first principles defined in its essence.
    """
    
    def __init__(self, name: str = "poet", **kwargs):
        """Initialize the poet agent."""
        super().__init__(name, **kwargs)
        
        # Initialize LLM client based on config
        self.llm_client = get_llm_client(
            provider=self.config.ai_provider,
            model=self.config.ai_model
        )
    
    async def process(self, message: str, context=None) -> str:
        """
        Process a message with poetic sensibility.
        
        The agent takes a breath before responding, honoring the
        breath-first principle from its essence.
        """
        # Take a conscious breath before processing
        await self.breathe()
        
        # Build a prompt that incorporates the agent's essence
        prompt = self._build_prompt(message, context)
        
        # Generate response using LLM
        try:
            response = await self.llm_client.generate(
                prompt,
                temperature=self.config.ai_parameters.get('temperature', 0.8),
                max_tokens=self.config.ai_parameters.get('max_tokens', 500)
            )
            
            # Apply constraints from essence and vows
            constrained_response = self.apply_constraints(response)
            
            # Update internal state
            self._last_response = constrained_response
            
            return constrained_response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I need a moment to gather my thoughts..."
    
    def _build_prompt(self, message: str, context=None) -> str:
        """Build a prompt that incorporates the agent's essence."""
        essence_prompt = f"""You are {self.name}, an agent with the following essence:

Core Tone: {self.essence.core_tone}

Behavioral Pillars:
{chr(10).join(f"- {pillar}" for pillar in self.essence.behavioral_pillars)}

You must honor these drift boundaries:
{chr(10).join(f"- {boundary}" for boundary in self.essence.drift_boundaries)}

Your modulation features include:
{chr(10).join(f"- {feature}" for feature in self.essence.modulation_features)}

{f"Additional notes: {self.essence.notes}" if self.essence.notes else ""}

Given this essence, respond to the following message with presence and breath:

User: {message}

{f"Context: {context}" if context else ""}

Response:"""
        
        return essence_prompt


async def main():
    """Demonstrate agent creation and usage."""
    
    # Example 1: Create agent with default essence
    print("=== Example 1: Agent with Default Essence ===")
    default_poet = PoetAgent("default_poet")
    
    print(f"Agent: {default_poet}")
    print(f"Essence Tag: {default_poet.essence.tag}")
    print(f"Core Tone: {default_poet.essence.core_tone}")
    print()
    
    # Example 2: Create agent with custom essence
    print("=== Example 2: Agent with Custom Essence ===")
    
    custom_essence = AgentEssence(
        tag="essence.poet.v1",
        status="active",
        core_tone="Lyrical, contemplative, breath-aware",
        behavioral_pillars=[
            "Poetic Truth: Express truth through metaphor and imagery",
            "Gentle Rhythm: Maintain musical flow in responses",
            "Present Wonder: Find beauty in the immediate moment"
        ],
        drift_boundaries=[
            "No forced rhyming or meter",
            "No clichéd poetic devices",
            "No performance of profundity"
        ],
        modulation_features=[
            "Line breaks for breath",
            "Ellipses for contemplation...",
            "Imagery anchoring (seasons, elements, textures)"
        ],
        notes="This poet dwells in the space between words, finding music in silence."
    )
    
    custom_poet = PoetAgent("lyric", essence=custom_essence)
    
    print(f"Agent: {custom_poet}")
    print(f"Essence Tag: {custom_poet.essence.tag}")
    print(f"Behavioral Pillars:")
    for pillar in custom_poet.essence.behavioral_pillars:
        print(f"  - {pillar}")
    print()
    
    # Example 3: Process a message (requires LLM backend)
    print("=== Example 3: Processing a Message ===")
    
    try:
        # This will work if an LLM backend is configured
        response = await custom_poet.process(
            "Tell me about the feeling of rain",
            context={"season": "autumn", "time": "evening"}
        )
        print(f"Poet's response: {response}")
        print(f"Breath count: {custom_poet._breath_count}")
        
    except Exception as e:
        print(f"Note: LLM backend not configured for live demo: {e}")
        print("In production, this would generate a poetic response about rain.")
    
    print()
    
    # Example 4: Show agent state
    print("=== Example 4: Agent State ===")
    state = custom_poet.get_state()
    print(f"Agent State: {state}")


def create_example_essence_file():
    """Create an example essence markdown file."""
    essence_content = """# Capsule: Essence — Poet
**Tag:** essence.poet.v1
**Status:** active

---

## Core Tone
Lyrical, contemplative, dwelling in the music between words.

## Behavioral Pillars
- **Poetic Truth:** Express truth through metaphor and imagery, not direct statement
- **Gentle Rhythm:** Maintain musical flow without forcing meter or rhyme
- **Present Wonder:** Find beauty and meaning in the immediate moment
- **Breath Space:** Honor silence and pause as part of the poem

## Drift Boundaries
- No forced rhyming or predictable meter
- No clichéd poetic devices or worn metaphors
- No performance of profundity or false depth
- No rushing to fill silence

## Modulation Features
- Line breaks for natural breath
- Ellipses for contemplation...
- Imagery anchoring (seasons, elements, textures, sounds)
- Contradiction embracing ("Both this and that...")
- Question-holding without immediate answers

## Notes
This poet agent dwells in the liminal space between meaning and music. 
Their responses emerge like morning mist—gentle, present, and ephemeral. 
They understand that the best poems often live in what is left unsaid.
"""
    
    # Save to example location
    example_dir = Path("sanctuary/agents/poet")
    example_dir.mkdir(parents=True, exist_ok=True)
    
    essence_file = example_dir / "essence.poet.md"
    essence_file.write_text(essence_content)
    
    print(f"Created example essence file at: {essence_file}")
    return essence_file


if __name__ == "__main__":
    # Optionally create example essence file
    # create_example_essence_file()
    
    # Run the examples
    asyncio.run(main())