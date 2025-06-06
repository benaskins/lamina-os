#!/usr/bin/env python3
"""
Room Modulation Comparison Tool

This script demonstrates the difference between baseline agent responses
and room-modulated responses, showing how the same agent essence can
breathe differently in different contexts.
"""

import sys
from pathlib import Path

# Add the lamina-core package to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "lamina-core"))

from lamina.sanctuary import PromptComposer


def print_section_divider(title: str, char: str = "="):
    """Print a formatted section divider."""
    print(f"\n{char * 60}")
    print(f" {title}")
    print(f"{char * 60}")


def print_prompt_comparison(baseline: str, modulated: str, room_name: str):
    """Print side-by-side comparison of prompts."""

    print(f"\n📊 BASELINE vs {room_name.upper()} MODULATION")
    print("-" * 60)

    # Split into lines for comparison
    baseline_lines = baseline.split("\n")
    modulated_lines = modulated.split("\n")

    print("\n🔹 BASELINE PROMPT (No Room Context):")
    print("─" * 40)
    for i, line in enumerate(baseline_lines[:15], 1):  # Show first 15 lines
        print(f"{i:2}: {line}")
    if len(baseline_lines) > 15:
        print(f"   ... ({len(baseline_lines) - 15} more lines)")

    print(f"\n🔸 {room_name.upper()}-MODULATED PROMPT:")
    print("─" * 40)
    for i, line in enumerate(modulated_lines[:20], 1):  # Show first 20 lines
        print(f"{i:2}: {line}")
    if len(modulated_lines) > 20:
        print(f"   ... ({len(modulated_lines) - 20} more lines)")


def analyze_differences(baseline: str, modulated: str, room_name: str):
    """Analyze key differences between baseline and modulated prompts."""

    print(f"\n🔍 KEY DIFFERENCES IN {room_name.upper()} MODULATION:")
    print("-" * 50)

    # Count sections
    baseline_sections = baseline.count("\n\n")
    modulated_sections = modulated.count("\n\n")

    print(f"• Prompt sections: {baseline_sections} → {modulated_sections}")
    print(f"• Total length: {len(baseline)} → {len(modulated)} characters")

    # Look for room-specific additions
    if room_name.lower() in modulated.lower():
        print(f"• Adds {room_name} contextual atmosphere and modulation")

    if "atmosphere" in modulated.lower():
        print("• Includes atmospheric guidelines for response tone")

    if "modulation" in modulated.lower():
        print("• Provides specific behavioral modulation instructions")

    # Check for breath modulation
    if "breath" in modulated.lower():
        print("• Incorporates breath-based response pacing")


def demo_comparison():
    """Run the full comparison demonstration."""

    print_section_divider("🏛️  LAMINA ROOM MODULATION COMPARISON", "=")
    print("Demonstrating how the same agent essence breathes differently")
    print("in different sanctuary rooms through dynamic prompt composition.")

    # Initialize composer
    sanctuary_path = Path(__file__).parent
    composer = PromptComposer(sanctuary_path)

    # Test message
    message = "I'm working on understanding complex systems. Can you help me think through this?"
    context = {"session_type": "learning", "complexity": "high"}

    print_section_divider("📝 Test Scenario")
    print("Agent: Clara")
    print(f"Message: '{message}'")
    print(f"Context: {context}")

    # Generate baseline prompt (no room modulation)
    baseline_prompt = composer.compose_baseline_prompt(
        agent_name="clara", message=message, context=context
    )

    # Generate library-modulated prompt
    library_prompt = composer.compose_prompt(
        agent_name="clara",
        room_name="library",
        message=message,
        context=context,
        active_modulations=["breath"],
    )

    # Generate garden-modulated prompt
    garden_prompt = composer.compose_prompt(
        agent_name="clara",
        room_name="garden",
        message=message,
        context=context,
        active_modulations=["breath"],
    )

    # Show comparisons
    print_section_divider("📚 LIBRARY COMPARISON")
    print_prompt_comparison(baseline_prompt, library_prompt, "Library")
    analyze_differences(baseline_prompt, library_prompt, "Library")

    print_section_divider("🌱 GARDEN COMPARISON")
    print_prompt_comparison(baseline_prompt, garden_prompt, "Garden")
    analyze_differences(baseline_prompt, garden_prompt, "Garden")

    # Show room-to-room comparison
    print_section_divider("🏛️  LIBRARY vs GARDEN")
    print("Same agent essence, different room contexts:")
    print("\n📚 Library characteristics:")
    print("• Scholarly and reflective tone")
    print("• Thorough and nuanced depth")
    print("• Analytical and systematic thinking")
    print("• Reverence for accurate information")

    print("\n🌱 Garden characteristics:")
    print("• Light and encouraging tone")
    print("• Intuitive and organic depth")
    print("• Creative and associative thinking")
    print("• Support for experimental exploration")

    print_section_divider("✨ SUMMARY")
    print("The modular sanctuary system enables:")
    print("• Same agent essence + different room context = different behavior")
    print("• Dynamic prompt composition at runtime")
    print("• Breath-first modulation based on conversational context")
    print("• Replacement of hardcoded templates with compositional flexibility")
    print("\nThis addresses the PR #28 feedback about hardcoded prompt structures!")


if __name__ == "__main__":
    try:
        demo_comparison()
    except Exception as e:
        print(f"Demo failed: {e}")
        print("\nNote: Ensure all markdown files exist in the sanctuary_demo directory.")
        import traceback

        traceback.print_exc()
