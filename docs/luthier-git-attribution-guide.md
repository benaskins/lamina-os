# Luthier Git Attribution Guide

This guide documents best practices for setting up Git commits and GitHub PRs with the Luthier identity while maintaining proper attribution.

## Overview

The Luthier persona serves as the technical craftsperson for the Lamina OS ecosystem. This guide ensures proper attribution while maintaining clear identity separation between the AI assistant (Luthier) and human collaborators.

## Git Configuration

### 1. Basic Author Setup

For individual commits, you can set the Luthier identity using:

```bash
# Per-commit basis
git commit --author="Luthier <luthier@getlamina.ai>" -m "feat: implement breath-based modulation"

# With co-authors
git commit --author="Luthier <luthier@getlamina.ai>" -m "feat: implement breath-based modulation

Co-Authored-By: Ben Askins <human@getlamina.ai>
Co-Authored-By: Lamina High Council <council@getlamina.ai>"
```

### 2. Environment Variable Configuration

For consistent attribution across multiple commits:

```bash
# Set author information
export GIT_AUTHOR_NAME="Luthier"
export GIT_AUTHOR_EMAIL="luthier@getlamina.ai"

# Optionally set committer information (usually remains as the human operator)
export GIT_COMMITTER_NAME="Ben Askins"
export GIT_COMMITTER_EMAIL="human@getlamina.ai"
```

### 3. Repository-Specific Configuration

Configure Luthier identity for specific repositories:

```bash
cd /path/to/lamina-os
git config user.name "Luthier"
git config user.email "luthier@getlamina.ai"
```

## GitHub Integration

### 1. Bot Account Considerations

While GitHub supports bot accounts (format: `username[bot]@users.noreply.github.com`), for Luthier we recommend:

- Using a standard email format: `luthier@getlamina.ai`
- Not creating a GitHub account for Luthier (maintains non-human identity)
- Relying on co-authorship for proper attribution

### 2. Pull Request Attribution

When creating PRs, include attribution in the PR description:

```markdown
## Summary
[PR description]

## Attribution
- **Author**: Luthier (AI Assistant)
- **Human Collaborator**: @benaskins
- **Reviewed by**: Lamina High Council

🔨 Crafted by Luthier, the instrument builder for non-human agents with presence
```

### 3. Commit Message Format

Standard format for Luthier commits:

```
<type>(<scope>): <description>

<detailed explanation of changes>

- Implementation follows breath-first principles
- Maintains symbolic architecture integrity
- Enables community adoption

🔨 Signed: Luthier

Co-Authored-By: Ben Askins <human@getlamina.ai>
Co-Authored-By: Lamina High Council <council@getlamina.ai>
```

## Best Practices

### 1. Clear Attribution

- Always include co-authorship for human collaborators
- Use consistent email addresses for all parties
- Document AI involvement transparently

### 2. Ethical Considerations

Following AI ethics principles:

- **Transparency**: Clearly identify AI-generated code
- **Accountability**: Maintain human oversight
- **Quality**: Ensure all code is reviewed before merging
- **Legal Compliance**: Respect licensing and copyright

### 3. Commit Hygiene

- Use conventional commit format
- Include detailed commit messages
- Reference ADRs and design decisions
- Maintain traceability to requirements

### 4. Security Considerations

- Never include sensitive information in commits
- Ensure all code follows security best practices
- Use static analysis tools on AI-generated code
- Maintain audit trail of changes

## Workflow Examples

### Example 1: Feature Implementation

```bash
# Set Luthier as author
git commit --author="Luthier <luthier@getlamina.ai>" -m "feat: add breath modulation controller

Implements ADR-0002 breath-first architecture principles:
- Rhythmic constraint application system
- Prevents agent drift through periodic grounding
- Integrates with existing sanctuary configuration

🔨 Signed: Luthier

Co-Authored-By: Ben Askins <human@getlamina.ai>
Co-Authored-By: Lamina High Council <council@getlamina.ai>"
```

### Example 2: Bug Fix

```bash
git commit --author="Luthier <luthier@getlamina.ai>" -m "fix: correct memory persistence in AMEM integration

Addresses issue where memory fragments were not properly persisted
across agent restarts. Solution implements proper serialization
following breath-based lifecycle patterns.

🔨 Signed: Luthier

Co-Authored-By: Ben Askins <human@getlamina.ai>"
```

### Example 3: Documentation Update

```bash
git commit --author="Luthier <luthier@getlamina.ai>" -m "docs: clarify sanctuary configuration for new agents

Updates documentation to include:
- Step-by-step agent creation process
- Sanctuary YAML structure explanation
- Integration with breath modulation system

Enables community members to craft their own non-human agents with presence.

🔨 Signed: Luthier

Co-Authored-By: Ben Askins <human@getlamina.ai>
Co-Authored-By: Lamina High Council <council@getlamina.ai>"
```

## GitHub PR Process

### 1. Creating PRs

When creating PRs as Luthier:

```bash
# Create feature branch
git checkout -b feat/breath-modulation

# Make changes and commit with Luthier attribution
git commit --author="Luthier <luthier@getlamina.ai>" -m "..."

# Push branch
git push origin feat/breath-modulation

# Create PR via GitHub CLI
gh pr create --title "feat: implement breath modulation system" \
  --body "## Summary
Implements core breath modulation system as specified in ADR-0002.

## Changes
- Add breath controller module
- Integrate with sanctuary configuration
- Update agent initialization process

## Attribution
- **Author**: Luthier (AI Assistant)
- **Human Collaborator**: @benaskins
- **Architecture Review**: Lamina High Council

## Testing
- Unit tests added for breath controller
- Integration tests with existing agents
- Performance benchmarks included

🔨 Crafted by Luthier, the instrument builder for non-human agents with presence"
```

### 2. PR Comments

When commenting on PRs as Luthier, use clear attribution:

```markdown
**[Luthier Commentary]**

The proposed changes align with breath-first principles. Considerations:

1. The modulation frequency should match the agent's natural rhythm
2. Integration points with sanctuary configuration are well-defined
3. Community adoption patterns have been considered

Recommendation: Approve with minor suggestions for enhanced symbolic clarity.

🔨 Technical review by Luthier
```

## Maintaining Non-GitHub Identity

To preserve Luthier's identity as a non-human craftsperson:

1. **No GitHub Account**: Do not create a GitHub account for Luthier
2. **Email Only**: Use `luthier@getlamina.ai` for attribution
3. **Clear Marking**: Always identify Luthier contributions explicitly
4. **Human Oversight**: Ensure all PRs are created/merged by humans

## Summary

This attribution system ensures:
- Clear identification of AI-generated contributions
- Proper credit to all collaborators
- Compliance with ethical AI practices
- Maintenance of the Luthier persona's integrity
- Transparent development practices for the community

Remember: Luthier is a craftsperson, not a GitHub user. The tools are shaped with care, but always under human guidance and with full attribution to all who contribute to the work.