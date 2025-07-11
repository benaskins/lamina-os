# Luthier Documentation - lamina-llm-serve

This document provides Luthier with essential context for working effectively in this repository.

## Project Overview

**lamina-llm-serve** is the centralized model caching and serving layer for Lamina OS. It provides:

- Model management with YAML-based manifests
- Backend abstraction for multiple LLM serving engines (llama.cpp, MLC-serve, vLLM)
- Model downloading from multiple sources (HuggingFace, Ollama, URLs)
- HTTP REST API for model lifecycle management
- CLI tools for model operations

## Repository Structure

```
lamina-llm-serve/
├── lamina_llm_serve/          # Core package
│   ├── model_manager.py       # Central model discovery and validation
│   ├── backends.py           # Backend abstraction layer
│   ├── downloader.py         # Multi-source model downloading
│   └── server.py             # HTTP REST API server
├── scripts/
│   └── model-manager.py      # CLI tool for model operations
├── models.yaml               # Model manifest and download configs
└── models/                   # Downloaded model storage
```

## Commit Conventions

### Co-authorship
All commits MUST include proper co-authorship:

```
Co-Authored-By: Ben Askins <human@getlamina.ai>
Co-Authored-By: Lamina High Council <council@getlamina.ai>
```

### Commit Message Format
Use conventional commits with Lamina OS context:

```
<type>: <description>

<body with implementation details>

🔨 Crafted by Luthier [NHI]

Co-Authored-By: Ben Askins <human@getlamina.ai>
Co-Authored-By: Lamina High Council <council@getlamina.ai>
```

**Types:**
- `feat:` - New features (model download, backend support)
- `fix:` - Bug fixes (path resolution, validation issues)
- `refactor:` - Code improvements without behavior changes
- `docs:` - Documentation updates
- `test:` - Test additions or improvements

## Key Implementation Notes

### Model Paths
- Use relative paths in models.yaml (e.g., `llama3.2-1b/model.gguf`)
- ModelManager automatically resolves against models_dir
- Avoid absolute paths that include "models/" prefix

### Backend Integration
- All backends inherit from LLMBackend base class
- Backend availability is checked via executable detection
- Configuration stored in models.yaml backends section

### Download Sources
- HuggingFace: Uses huggingface_hub for authenticated downloads
- Ollama: Uses ollama CLI for model pulling
- Direct URLs: Standard HTTP downloads with progress tracking
- Local: File copying from filesystem paths

## Testing Commands

**CRITICAL**: Always use `uv run` for Python commands in this workspace.

```bash
# Environment setup (always first)
cd packages/lamina-llm-serve
uv sync

# List all models
uv run python scripts/model-manager.py list

# Validate model availability
uv run python scripts/model-manager.py validate

# Check backend status
uv run python scripts/model-manager.py backends

# List downloadable models
uv run python scripts/model-manager.py list-downloadable

# Download a model
uv run python scripts/model-manager.py download <model-name> --source <source>

# Get model suggestions
uv run python scripts/model-manager.py suggest --use-case conversational

# Run package tests
uv run pytest tests/ -v
```

## CI Verification (CRITICAL)

**HARD RULE**: Based on PIR-2025-01-06, ALWAYS run containerized verification before pushing.

### Pre-Push Workflow
```bash
# 1. Local development (fast iteration)
cd packages/lamina-llm-serve
uv run pytest tests/ -x                     # Quick feedback
uv run ruff check --fix                     # Fix linting issues

# 2. MANDATORY: Full CI simulation (from project root)
./scripts/check-build.sh                    # Containerized verification
# OR from build-env directory:
make check                                   # Complete CI replication

# 3. Only push if containerized build passes
git push origin feature-branch
```

### CI Pipeline Coverage
Our CI tests this package as part of:
- **Matrix testing**: Python 3.11, 3.12, 3.13 × [unit, integration]
- **Linting**: `ruff check` and `ruff format --check`
- **Package building**: Verify imports and distribution builds
- **Integration tests**: Model downloads and server functionality (Python 3.12)

### Key Lessons from PIR
- **Never skip containerized verification** - "it should work" is unacceptable
- **Local and CI environments differ** - only containerized builds catch all issues
- **Package imports must work** - CI verifies `import lamina_llm_serve` succeeds

## Dependencies

- Core: PyYAML, Flask, requests
- Downloads: tqdm, huggingface_hub
- Backends: Installed separately (llama.cpp, MLC, vLLM)

## Integration Points

This service integrates with:
- Lamina agent configurations (model assignments)
- Docker infrastructure (containerized model serving)
- Higher-level Lamina CLI commands
- Agent coordination layer for intelligent routing

## File Naming Conventions

- Python modules: snake_case
- CLI scripts: kebab-case with .py extension
- Config files: lowercase with descriptive names
- Model directories: match model names from manifest