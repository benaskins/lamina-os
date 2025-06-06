# Sanctuary Room Modulation Comparison

This directory demonstrates the difference between hardcoded agent prompts and dynamic room modulation in the Lamina sanctuary system.

## What This Demonstrates

The core issue from PR #28 was that **prompt structure is hardcoded in each agent**. This sanctuary demo shows how the same agent essence can "breathe differently" in different contexts through dynamic prompt composition.

## Directory Structure

```
sanctuary_demo/
├── agents/
│   └── clara.md              # Agent essence definition
├── rooms/
│   ├── library.md            # Scholarly, contemplative context
│   └── garden.md             # Creative, playful context
├── modulation/
│   └── breath.md             # Breath-based modulation rules
├── compare_modulation.py     # Side-by-side prompt comparison
├── modulation_analyzer.py    # Detailed modulation analysis
├── demo_dynamic_composition.py  # Basic composition demo
└── README.md                 # This file
```

## Running the Comparisons

### 1. Basic Composition Demo
```bash
uv run python demo_dynamic_composition.py
```
Shows how the same agent behaves differently in Library vs Garden contexts.

### 2. Side-by-Side Comparison
```bash
uv run python compare_modulation.py
```
Compares baseline (no room) vs room-modulated prompts, showing:
- Character count differences
- Section additions
- Atmospheric and behavioral changes

### 3. Detailed Analysis
```bash
uv run python modulation_analyzer.py
```
Deep analysis of specific modulation elements:
- Atmospheric additions
- Behavioral modulation rules
- Breath-aware elements
- Tone changes
- Predicted response differences

## Key Differences Demonstrated

### Baseline (No Room Context)
- Just agent essence + constraints
- Generic, hardcoded-style behavior
- ~1,600 characters
- 8 prompt sections

### Library Modulation
- Adds scholarly, contemplative atmosphere
- Analytical and systematic thinking mode
- Thorough and nuanced depth
- References to sources and methodologies
- ~2,850 characters
- 16 prompt sections

### Garden Modulation  
- Adds creative, encouraging atmosphere
- Creative and associative thinking mode
- Intuitive and organic depth
- High support for creative exploration
- ~2,850 characters
- 16 prompt sections

## The Solution to Hardcoded Prompts

Instead of each agent having a hardcoded prompt template, the sanctuary system:

1. **Composes dynamically** - Prompts assembled at runtime from modular components
2. **Enables context breathing** - Same agent essence + different room = different behavior
3. **Supports modulation** - Breath-based rules and atmospheric guidelines
4. **Maintains consistency** - Agent core essence preserved across contexts
5. **Scales naturally** - New rooms/modulation rules don't require agent changes

This addresses the PR #28 feedback by replacing monolithic, hardcoded prompt structures with compositional, context-aware prompt assembly.

## Architecture Benefits

- **Modularity** - Agent essence, rooms, and modulation rules are separate
- **Reusability** - Same components work across different agents
- **Extensibility** - New rooms add context without changing agent code
- **Breath-first** - Enables conscious, context-aware AI behavior
- **Maintainability** - Changes to room behavior don't affect agent essence

The result is truly modular, breath-first AI that can adapt its behavior to conversational context while maintaining core identity.