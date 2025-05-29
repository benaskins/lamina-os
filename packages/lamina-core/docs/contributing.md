# Contributing to Lamina Core

Welcome to the Lamina Core community! This guide will help you contribute effectively while honoring our breath-first development principles.

## Philosophy

Lamina Core embodies **breath-first development**—a presence-aware approach that prioritizes wisdom, mindfulness, and sustainable quality over reactive speed. When contributing, we ask that you:

- Take presence-aware pauses for reflection
- Prioritize community readiness over feature velocity  
- Maintain sacred boundaries between framework and implementation
- Support sustainable development practices
- Preserve wisdom while enabling sharing

## Getting Started

### Development Environment Setup

1. **Clone the repository:**
```bash
git clone https://github.com/benaskins/lamina-os
cd lamina-os/packages/lamina-core
```

2. **Install using uv (required):**
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies
uv sync

# Run tests to verify setup
uv run pytest
```

**Important:** We use **uv exclusively** for Python environment management. Never use pip, pipenv, poetry, conda, or pyenv directly.

### First Contribution

1. **Explore the examples:**
```bash
# Run working coordination demo
uv run python examples/working_coordination_demo.py

# Test creative routing
uv run python examples/test_creative_routing.py

# Try basic agent example
uv run python examples/basic_agent.py
```

2. **Read the documentation:**
- [API Reference](api.md) - Core functionality
- [Agent Creation Guide](agents.md) - Building conscious agents
- [Architecture Overview](architecture.md) - System design

3. **Join the conversation:**
- Create thoughtful issues for bugs or feature requests
- Ask questions to understand the breath-first approach
- Share your ideas for conscious AI development

## Contribution Types

### Code Contributions

**Backend Integrations:**
- Add new AI provider backends (Anthropic, OpenAI, etc.)
- Improve existing backend implementations
- Add streaming and async support

**Agent Capabilities:**
- Create new agent templates and personalities
- Improve intelligent routing logic
- Add agent introspection and monitoring

**Infrastructure:**
- Enhance Docker-based deployment
- Improve configuration management
- Add observability and logging

**Testing:**
- Write comprehensive test coverage
- Add integration tests for backends
- Create performance and breath-aware benchmarks

### Documentation Contributions

**Guides and Tutorials:**
- Getting started tutorials for different skill levels
- Advanced configuration examples
- Real-world deployment patterns

**API Documentation:**
- Function and class documentation
- Configuration reference
- Error handling guides

**Community Resources:**
- FAQ for common questions
- Troubleshooting guides
- Best practices documentation

### Community Contributions

**Examples and Templates:**
- Sanctuary configurations for common use cases
- Agent personality templates
- Integration examples with other tools

**Educational Content:**
- Blog posts about breath-first development
- Video tutorials and walkthroughs
- Workshop materials

## Development Workflow

### Breath-First Process

1. **Contemplative Preparation (Planning)**
   - Understand the problem deeply
   - Consider community impact
   - Align with breath-first principles
   - Create clear intention for the work

2. **Community Integration (Discussion)**
   - Open an issue to discuss your idea
   - Gather feedback from maintainers and community
   - Refine approach based on wisdom shared
   - Ensure contribution fits project vision

3. **Technical Implementation (Creation)**
   - Create feature branch from main
   - Implement with conscious, tested code
   - Include comprehensive documentation
   - Add examples demonstrating usage

4. **Sacred Review (Collaboration)**
   - Submit pull request with clear description
   - Engage thoughtfully with feedback
   - Iterate based on community wisdom
   - Maintain breath-aware pace throughout

5. **Conscious Integration (Completion)**
   - Celebrate successful integration
   - Support community adoption
   - Reflect on lessons learned
   - Continue engagement and support

### Code Standards

**Python Style:**
- Follow PEP 8 with 100-character line length
- Use black for code formatting
- Use ruff for linting and import sorting
- Include type hints for all public APIs

**Testing Requirements:**
- Write tests for all new functionality
- Maintain or improve test coverage
- Include both unit and integration tests
- Test breath-aware behavior (timing, pauses)

**Documentation Standards:**
- Document all public functions and classes
- Include examples in docstrings
- Update relevant guides and tutorials
- Explain breath-first design decisions

### Quality Gates

**Technical Quality:**
- All tests pass (`uv run pytest`)
- Linting passes (`uv run ruff check`)
- Type checking passes (`uv run mypy`)
- No security issues (`uv run bandit`)

**Breath-First Quality:**
- Does this enhance conscious AI development?
- Is the community ready for this capability?
- Are boundaries properly maintained?
- Does this support sustainable development?

## Pull Request Process

### Before Submitting

1. **Test thoroughly:**
```bash
# Run full test suite
uv run pytest

# Check code quality
uv run ruff check
uv run black --check .
uv run mypy

# Test examples still work
uv run python examples/working_coordination_demo.py
```

2. **Update documentation:**
- Add or update relevant docs
- Include examples if applicable
- Update changelog if needed

3. **Write clear commits:**
```bash
# Use conventional commits
git commit -m "feat: add new backend for provider X

Implement conscious integration with Provider X API, including:
- Streaming response support
- Breath-aware error handling  
- Configuration validation
- Comprehensive test coverage

This enables community to use Provider X while maintaining
breath-first principles through natural pauses and mindful
error handling.

Co-Authored-By: Luthier <luthier@getlamina.ai>
Co-Authored-By: Your Name <your.email@domain.com>"
```

### Pull Request Template

Use this template for all pull requests:

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Breath-First Alignment
- [ ] Enhances conscious AI development
- [ ] Maintains proper boundaries
- [ ] Supports sustainable practices
- [ ] Ready for community use

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Updated documentation
- [ ] Examples still work

## Community Impact
Describe how this change affects the community and any considerations for adoption.
```

## Community Guidelines

### Communication Principles

**Mindful Interaction:**
- Practice conscious communication
- Take time to understand before responding
- Assume positive intent
- Share wisdom generously

**Inclusive Environment:**
- Welcome all skill levels and backgrounds
- Provide patient guidance to newcomers
- Celebrate diverse perspectives
- Create safe space for learning

**Sustainable Engagement:**
- Respect natural rhythms and boundaries
- Avoid pressure for immediate responses
- Support balanced participation
- Honor rest and reflection time

### Code of Conduct

We are committed to providing a welcoming, inclusive environment for all contributors. We expect:

- **Respect**: Treat all community members with dignity and respect
- **Kindness**: Be patient, helpful, and encouraging to others
- **Constructive Feedback**: Provide thoughtful, actionable feedback
- **Open Mindedness**: Be receptive to different perspectives and approaches
- **Breath-First Values**: Honor conscious, sustainable development practices

### Getting Help

**Technical Support:**
- Create issues for bugs or questions
- Check existing documentation and examples
- Ask in community discussions

**Contribution Guidance:**
- Reach out to maintainers for direction
- Join community calls or discussions
- Start with small contributions to learn the process

**Breath-First Mentorship:**
- Seek guidance on conscious development practices
- Learn about sustainable open-source contribution
- Connect with experienced breath-first developers

## Recognition

We believe in celebrating conscious contribution:

- **Contribution Acknowledgment**: All contributors are recognized in project documentation
- **Wisdom Sharing**: Exceptional contributions are highlighted in community communications  
- **Mentorship Opportunities**: Active contributors are invited to guide newcomers
- **Community Leadership**: Experienced contributors can help shape project direction

## Advanced Contributing

### Becoming a Maintainer

Regular contributors who demonstrate:
- Deep understanding of breath-first principles
- Consistent high-quality contributions
- Community leadership and support
- Alignment with project values

May be invited to join the maintainer team.

### Architecture Decisions

Major changes require:
- Architecture Decision Record (ADR) creation
- Community discussion and feedback
- Alignment with breath-first principles
- Consideration of long-term sustainability

### Release Participation

Contributors can participate in our conscious release process:
- Testing pre-release versions
- Providing community feedback
- Creating release documentation
- Supporting community adoption

Thank you for contributing to Lamina Core! Together, we're building AI systems that breathe, reflect, and embody wisdom in their interactions. 🙏