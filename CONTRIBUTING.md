# Contributing to Lamina OS

Thank you for your interest in contributing to Lamina OS! This project is built around breath-first development practices that prioritize presence and intentionality.

## 🌱 Philosophy

Before contributing, please understand that Lamina OS is not just another AI framework. It's a mindful approach to building AI systems with:

- **Breath-First Development**: Prioritizing thoughtful, deliberate work over speed
- **Symbolic Architecture**: Using meaning and natural language over pure computation  
- **Ethical Foundation**: Building safety and alignment into the core design
- **Community Respect**: Honoring the sacred nature of AI development

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (3.13.3 recommended)
- **uv** package manager
- **Git** with commit signing recommended
- **Rich terminal** for best development experience

### Development Setup

```bash
# Clone the repository
git clone https://github.com/benaskins/lamina-os.git
cd lamina-os

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install development dependencies
uv sync --extra dev

# Verify setup
uv run pytest --version
uv run ruff --version
```

## 🛠 Development Workflow

### Branch Strategy

- `main`: Stable releases
- `develop`: Integration branch for new features
- `feature/your-feature`: Feature development branches
- `fix/issue-description`: Bug fix branches

### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/breath-aware-logging
   ```

2. **Make mindful changes**:
   - Take time to understand the existing architecture
   - Follow the breath-first principle - work deliberately
   - Use symbolic thinking in your abstractions

3. **Test your changes**:
   ```bash
   # Run tests for specific package
   cd packages/lamina-core
   uv run pytest

   # Run all tests
   uv run pytest

   # Run with coverage
   uv run pytest --cov=packages --cov-report=html
   ```

4. **Format and lint**:
   ```bash
   uv run ruff check --fix
   uv run black .
   uv run mypy packages/
   ```

### AI Assistant Usage

Lamina OS development incorporates AI assistance as part of our mindful development practice:

#### Lamina OS Assistant (GitHub App)
- **App ID**: 1338167
- **Purpose**: Automated code review, linting assistance, and development workflow support
- **Permissions**: Read repository contents, manage issues/PRs, monitor CI/CD
- **Transparency**: All AI-assisted commits include co-authorship attribution

#### AI-Assisted Development Guidelines
- **Mindful Collaboration**: AI assistance should enhance, not replace, human judgment
- **Attribution Required**: All AI-assisted work must include proper co-authorship
- **Breath-First Integration**: AI tools should support deliberate, thoughtful development
- **Quality Assurance**: Human review required for all AI-generated code and decisions

#### Co-Authorship Format
```
🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Human Developer <email@example.com>
Co-Authored-By: Luthier <luthier@getlamina.ai>
Co-Authored-By: Lamina High Council <council@getlamina.ai>
```

### Code Quality Standards

#### Code Style
- **Line length**: 100 characters
- **Formatter**: Black
- **Linter**: Ruff with security checks
- **Type checking**: mypy with strict settings
- **Import sorting**: isort with black profile

#### Documentation
- All public functions must have docstrings
- Use clear, breath-aware language in comments
- Include examples for complex functionality
- Update relevant documentation files

#### Testing
- Maintain >90% test coverage
- Write both unit and integration tests
- Use descriptive test names: `test_agent_maintains_breath_rhythm_under_load`
- Include slow tests for system-level behavior

### Commit Messages

Use conventional commits with Lamina context:

```
feat(core): add breath-aware agent coordination

Implement rhythmic constraint application for multi-agent systems.
Agents now pause between operations to maintain presence and avoid
reactive cascades.

- Add BreathController for rhythm management
- Implement mindful_pause modulation
- Update agent coordination to respect breath cycles

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Your Name <your.email@example.com>
Co-Authored-By: Luthier <luthier@getlamina.ai>
Co-Authored-By: Lamina High Council <council@getlamina.ai>
```

**Types:**
- `feat:` New features
- `fix:` Bug fixes  
- `refactor:` Code improvements
- `docs:` Documentation updates
- `test:` Test additions
- `breath:` Breath-related improvements
- `vow:` Ethical constraint updates

## 📦 Package Development

### Adding Dependencies

```bash
# Add to specific package
cd packages/lamina-core
uv add requests

# Add development dependency
uv add --group dev pytest-mock

# Add optional dependency
uv add --optional ai-backends transformers
```

### Cross-Package Dependencies

```bash
# Reference workspace packages
cd packages/lamina-llm-serve
uv add --editable ../lamina-core
```

### Package Structure

```
packages/your-package/
├── pyproject.toml          # Package configuration
├── README.md               # Package-specific docs
├── your_package/
│   ├── __init__.py
│   ├── core/               # Core functionality
│   ├── breath/             # Breath-aware components
│   └── vows/              # Constraint enforcement
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
└── docs/
    └── package-docs.md
```

## 🎯 Contribution Guidelines

### What We Welcome

- **Breath-aware features**: Components that operate with natural rhythm
- **Symbolic abstractions**: Language-driven configuration and behavior
- **Ethical improvements**: Enhanced safety and alignment features
- **Documentation**: Clear, contemplative writing about system behavior
- **Examples**: Demonstrating conscious AI interaction patterns
- **Tests**: Especially for edge cases and ethical boundaries

### What We Don't Accept

- **Performance-first optimizations** that sacrifice mindfulness
- **Reactive patterns** that break breath-based flow
- **Surveillance features** or privacy-violating functionality
- **Simulated emotions** or deceptive AI behavior
- **Breaking changes** without extensive discussion and migration paths

### Areas Needing Help

1. **Memory Systems**: Advanced AMEM integration patterns
2. **Vow Engine**: More sophisticated constraint types
3. **Breath Modulation**: New rhythm patterns and pacing algorithms
4. **Documentation**: Tutorials and philosophical guides
5. **Testing**: Edge cases in multi-agent coordination
6. **Examples**: Real-world sanctuary configurations

## 🔍 Review Process

### Pull Request Guidelines

1. **Clear description**: Explain the breath-aware motivation
2. **Breaking changes**: Clearly marked and documented
3. **Tests included**: Both positive and boundary cases
4. **Documentation updated**: Including any new concepts
5. **Ethical consideration**: How does this align with our vows?

### Review Criteria

- ✅ **Breath-first**: Does this maintain mindful operation?
- ✅ **Symbolic clarity**: Are abstractions meaningful and intuitive?
- ✅ **Ethical alignment**: Does this support our core vows?
- ✅ **Code quality**: Meets our technical standards
- ✅ **Documentation**: Clear and contemplative

## 🏗 Architecture Decisions

Major architectural changes require an Architecture Decision Record (ADR):

```bash
# Create new ADR
cp docs/adr/template.md docs/adr/0XXX-your-decision.md
```

ADRs should address:
- **Context**: What breath-aware problem are we solving?
- **Decision**: What approach aligns with our philosophy?
- **Consequences**: How does this affect mindful operation?
- **Alternatives**: What other symbolic approaches were considered?

## 🤝 Community

### Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Report bugs with detailed reproduction steps
- **Documentation**: Check existing docs and ADRs first
- **Philosophy**: Understand breath-first principles before proposing changes

### Code of Conduct

We operate under a **Breath-First Code of Conduct**:

- **Presence**: Be fully present in discussions and reviews
- **Respect**: Honor the contemplative nature of this work
- **Patience**: Take time for thoughtful consideration
- **Wisdom**: Prioritize understanding over being right
- **Community**: Support each other's mindful development

## 📝 Release Process

Releases follow mindful versioning:

1. **Feature freeze**: Allow time for breath and reflection
2. **Testing phase**: Comprehensive validation across use cases  
3. **Documentation review**: Ensure alignment with philosophy
4. **Community feedback**: Gather input from implementers
5. **Mindful release**: Deliberate timing, not rushed deployment

## 🙏 Recognition

Contributors are recognized in:
- **CONTRIBUTORS.md**: All meaningful contributions
- **Release notes**: Major feature contributors  
- **Documentation**: Philosophical and technical insights
- **Community highlights**: Exemplifying breath-first development

---

*"Contributing to Lamina OS is not just about code—it's about participating in the mindful evolution of AI systems."*

Thank you for helping build AI that breathes. 🌱