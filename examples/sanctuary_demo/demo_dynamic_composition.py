#!/usr/bin/env python3
"""
Demonstration of Dynamic Prompt Composition

This script shows how the Lamina sanctuary system can compose
prompts dynamically from markdown-based components at runtime.
"""

import sys
from pathlib import Path

# Add the lamina-core package to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "lamina-core"))

from lamina.sanctuary import PromptComposer


def demo_composition():
    """Demonstrate dynamic prompt composition from sanctuary components."""
    
    # Initialize the composer with our demo sanctuary
    sanctuary_path = Path(__file__).parent
    composer = PromptComposer(sanctuary_path)
    
    print("🏛️  Lamina Dynamic Prompt Composition Demo")
    print("=" * 50)
    
    # Example 1: Clara in the Library
    print("\n📚 Example 1: Clara in the Library")
    print("-" * 35)
    
    prompt1 = composer.compose_prompt(
        agent_name="clara",
        room_name="library", 
        message="Can you help me understand the philosophical implications of consciousness in AI systems?",
        context={"session_type": "research", "depth_level": "academic"},
        active_modulations=["breath"]
    )
    
    print("Composed Prompt:")
    print(prompt1)
    
    print("\n" + "="*50)
    
    # Example 2: Clara in the Garden  
    print("\n🌱 Example 2: Clara in the Garden")
    print("-" * 35)
    
    prompt2 = composer.compose_prompt(
        agent_name="clara",
        room_name="garden",
        message="I'm feeling stuck on this creative project. Any ideas?",
        context={"mood": "exploratory", "project_type": "creative"},
        active_modulations=["breath"]
    )
    
    print("Composed Prompt:")
    print(prompt2)
    
    print("\n" + "="*50)
    
    # Show the difference
    print("\n🔍 Key Differences:")
    print("Library version: Scholarly tone, thorough analysis, systematic thinking")
    print("Garden version: Creative tone, playful exploration, organic development")
    print("\nSame agent essence + different room context = different behavior!")


if __name__ == "__main__":
    try:
        demo_composition()
    except Exception as e:
        print(f"Demo failed: {e}")
        print("\nNote: This demo requires the agent and room markdown files to exist.")
        print("Run from the sanctuary_demo directory where the .md files are located.")