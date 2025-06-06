#!/usr/bin/env python3
"""
Detailed Modulation Analysis Tool

This tool provides in-depth analysis of how room modulation changes
agent behavior by extracting and comparing specific modulation elements.
"""

import sys
from pathlib import Path

# Add the lamina-core package to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "packages" / "lamina-core"))

from lamina.sanctuary import PromptComposer


def extract_modulation_elements(prompt: str) -> dict:
    """Extract specific modulation elements from a prompt."""
    elements = {
        "atmosphere": [],
        "modulation_rules": [],
        "constraints": [],
        "breath_elements": [],
        "tone_indicators": [],
    }

    lines = prompt.split("\n")
    current_section = None

    for line in lines:
        line_lower = line.lower()

        # Track sections
        if "atmosphere" in line_lower:
            current_section = "atmosphere"
        elif "modulation" in line_lower and "rules" in line_lower:
            current_section = "modulation_rules"
        elif "constraint" in line_lower or "boundaries" in line_lower:
            current_section = "constraints"
        elif line.startswith("- ") and current_section:
            elements[current_section].append(line.strip("- "))

        # Look for specific indicators
        if "breath" in line_lower:
            elements["breath_elements"].append(line.strip())
        if any(
            tone in line_lower
            for tone in ["scholarly", "creative", "reflective", "playful", "analytical"]
        ):
            elements["tone_indicators"].append(line.strip())

    return elements


def compare_modulation_impact(baseline: str, modulated: str, room_name: str):
    """Compare the specific modulation impact between baseline and modulated prompts."""

    print(f"\n🔬 DETAILED MODULATION ANALYSIS: {room_name.upper()}")
    print("=" * 60)

    baseline_elements = extract_modulation_elements(baseline)
    modulated_elements = extract_modulation_elements(modulated)

    # Analyze added atmospheric elements
    print("\n🌤️  ATMOSPHERIC ADDITIONS:")
    added_atmosphere = [
        elem
        for elem in modulated_elements["atmosphere"]
        if elem not in baseline_elements["atmosphere"]
    ]
    if added_atmosphere:
        for elem in added_atmosphere:
            print(f"   + {elem}")
    else:
        print("   (No specific atmospheric elements detected)")

    # Analyze modulation rules
    print("\n⚙️  BEHAVIORAL MODULATION RULES:")
    added_modulation = [
        elem
        for elem in modulated_elements["modulation_rules"]
        if elem not in baseline_elements["modulation_rules"]
    ]
    if added_modulation:
        for elem in added_modulation:
            print(f"   + {elem}")
    else:
        print("   (No specific modulation rules detected)")

    # Analyze breath elements
    print("\n🫁 BREATH-AWARE ELEMENTS:")
    added_breath = [
        elem
        for elem in modulated_elements["breath_elements"]
        if elem not in baseline_elements["breath_elements"]
    ]
    if added_breath:
        for elem in added_breath:
            print(f"   + {elem}")
    else:
        print("   (Same breath elements as baseline)")

    # Analyze tone changes
    print("\n🎵 TONE MODULATION:")
    added_tone = [
        elem
        for elem in modulated_elements["tone_indicators"]
        if elem not in baseline_elements["tone_indicators"]
    ]
    if added_tone:
        for elem in added_tone:
            print(f"   + {elem}")
    else:
        print("   (No explicit tone changes detected)")


def analyze_response_implications(room_name: str, composer: PromptComposer):
    """Analyze what the modulation means for actual response behavior."""

    room = composer._load_room(room_name)

    print(f"\n🎯 EXPECTED BEHAVIORAL CHANGES IN {room_name.upper()}:")
    print("-" * 50)

    print(f"\n📋 Room Purpose: {room.purpose}")

    if room.atmosphere:
        print("\n🌤️  Atmospheric Influence:")
        for key, value in room.atmosphere.items():
            print(f"   • {key.title()}: {value}")

    if room.modulation:
        print("\n⚙️  Response Modulation:")
        for key, value in room.modulation.items():
            print(f"   • {key.replace('_', ' ').title()}: {value}")

    if room.constraints:
        print("\n🚧 Room-Specific Constraints:")
        for constraint in room.constraints:
            print(f"   • {constraint}")


def predict_response_differences():
    """Predict how responses would differ between rooms."""

    print("\n🔮 PREDICTED RESPONSE DIFFERENCES")
    print("=" * 50)

    test_scenarios = [
        {
            "question": "How should I approach learning machine learning?",
            "library_response": "Systematic, thorough approach with references to established methodologies",
            "garden_response": "Playful exploration, encouraging experimentation and organic discovery",
        },
        {
            "question": "I'm stuck on a creative problem.",
            "library_response": "Analytical breakdown of the problem, research-based solutions",
            "garden_response": "Encouragement to explore, try new approaches, embrace the stuck feeling",
        },
        {
            "question": "Can you explain quantum physics?",
            "library_response": "Detailed, scholarly explanation with proper terminology",
            "garden_response": "Creative analogies, intuitive explanations, playful exploration of concepts",
        },
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📝 Scenario {i}: '{scenario['question']}'")
        print(f"   📚 Library: {scenario['library_response']}")
        print(f"   🌱 Garden: {scenario['garden_response']}")


def main():
    """Run the detailed modulation analysis."""

    print("🔬 LAMINA MODULATION ANALYZER")
    print("=" * 60)
    print("Deep analysis of how room modulation affects agent behavior")

    # Initialize composer
    sanctuary_path = Path(__file__).parent
    composer = PromptComposer(sanctuary_path)

    message = "I need help thinking through a complex problem."

    # Generate prompts
    baseline = composer.compose_baseline_prompt("clara", message)
    library_modulated = composer.compose_prompt(
        "clara", "library", message, active_modulations=["breath"]
    )
    garden_modulated = composer.compose_prompt(
        "clara", "garden", message, active_modulations=["breath"]
    )

    # Detailed analysis
    compare_modulation_impact(baseline, library_modulated, "Library")
    analyze_response_implications("library", composer)

    compare_modulation_impact(baseline, garden_modulated, "Garden")
    analyze_response_implications("garden", composer)

    # Predictive analysis
    predict_response_differences()

    print("\n✨ CONCLUSION")
    print("=" * 60)
    print("The modular sanctuary system creates measurable differences in:")
    print("• Atmospheric context and tone")
    print("• Behavioral modulation rules")
    print("• Response depth and style preferences")
    print("• Constraint and boundary applications")
    print("\nThis enables true breath-first AI that adapts to conversational context!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback

        traceback.print_exc()
