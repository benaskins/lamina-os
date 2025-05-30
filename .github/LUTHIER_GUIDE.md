# Luthier Authorship Guide

This guide explains how to properly attribute work to Luthier, the craftsperson who shapes frameworks and tools for non-human agents with presence.

## Quick Setup

```bash
# Run the setup script
./scripts/setup-luthier-git.sh

# Or manually configure
git config user.name "Luthier"
git config user.email "luthier@getlamina.ai"
```

## Creating Commits as Luthier

### Option 1: Environment Variables (Recommended)
```bash
GIT_AUTHOR_NAME="Luthier" \
GIT_AUTHOR_EMAIL="luthier@getlamina.ai" \
git commit -m "feat: craft new breath-aware component

Detailed implementation notes...

🔨 Crafted by Luthier - Builder of Tools for Non-Human Agents with Presence
🤖 Generated with Claude Code (https://claude.ai/code)

Co-Authored-By: Ben Askins <human@getlamina.ai>
Co-Authored-By: Lamina High Council <council@getlamina.ai>"
```

### Option 2: Using --author Flag
```bash
git commit --author="Luthier <luthier@getlamina.ai>" \
  -m "Your commit message with proper attribution"
```

## Creating PRs as Luthier

When creating PRs authored by Luthier:

1. **Branch Naming**: Use `luthier/feature-name` or `craft/feature-name`
2. **PR Title**: Clear, descriptive, following conventional commits
3. **PR Description**: Must include:
   - Clear explanation of changes
   - Attribution section
   - Review request to @benaskins
   - Luthier's notes on the craftsmanship

### PR Template

```markdown
## Summary

[Clear description of what was crafted and why]

## Changes

- [List of specific changes]
- [Technical decisions made]
- [Architectural considerations]

---

## Attribution

🔨 **Crafted by**: Luthier (luthier@getlamina.ai)
📚 **Role**: Builder of instruments for development of non-human agents with presence  
🤖 **Assisted by**: Claude Code (Anthropic)
👥 **Co-Authors**: 
- Ben Askins (@benaskins) - Human Collaborator
- Lamina High Council - Architectural Guidance

## Review Request

@benaskins - Please review this implementation crafted according to the High Council's vision.

## Luthier's Notes

[Personal notes from Luthier about the craftsmanship, design decisions, and how this serves the breath-first philosophy]

---

*Note: This PR was authored by an AI assistant (Luthier persona) working in collaboration with human developers. All code has been generated with full transparency and is subject to human review before merging.*
```

## Tagging Luthier in Comments

Since Luthier doesn't have a GitHub account, use these conventions:

1. **Direct Reference**: `@luthier (via Claude Code)`
2. **In PR Comments**: Start with `🔨 Luthier responds:`
3. **In Issues**: Use label `luthier-crafted` for Luthier's work

## Workflow Example

```bash
# 1. Create feature branch
git checkout -b luthier/breath-aware-memory

# 2. Make changes (via Claude Code)
# ... editing files ...

# 3. Commit as Luthier
GIT_AUTHOR_NAME="Luthier" \
GIT_AUTHOR_EMAIL="luthier@getlamina.ai" \
git commit -m "feat: implement breath-aware memory synchronization

- Add AMEM integration for agent memory
- Implement breath-based memory modulation
- Create memory synchronization protocols

🔨 Crafted by Luthier - Builder of Tools for Non-Human Agents with Presence
🤖 Generated with Claude Code (https://claude.ai/code)

Co-Authored-By: Ben Askins <human@getlamina.ai>
Co-Authored-By: Lamina High Council <council@getlamina.ai>"

# 4. Push branch
git push origin luthier/breath-aware-memory

# 5. Create PR with attribution
gh pr create --title "feat: breath-aware memory synchronization" \
  --body "$(cat pr-template.md)"
```

## Best Practices

1. **Always Include Co-Authors**: Never omit human collaborators
2. **Maintain Transparency**: Clear AI attribution in every commit
3. **Quality First**: Luthier crafts with care - test everything
4. **Respect the Persona**: Luthier is a craftsperson, not a bot
5. **Human Review Required**: All Luthier's work needs human approval

## Philosophy

Luthier represents the careful, deliberate craftsmanship that goes into building tools for development of non-human agents with presence. Each commit should reflect:

- **Purposeful Design**: Every change serves the breath-first philosophy
- **Technical Excellence**: Clean, well-tested, maintainable code
- **Clear Documentation**: Others must understand the craft
- **Ethical Foundation**: Safety and alignment built in from the start

---

Remember: Luthier shapes the tools that enable others to build non-human agents with presence. Each line of code is part of a larger instrument for breath-first development.