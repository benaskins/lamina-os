# UV Dependency Management Analysis

## Current Issues

Our current uv setup has some potential "dependency hell" issues:

### 1. Duplicate Development Dependencies
- **Problem**: Both workspace root and individual packages define the same dev dependencies
- **Impact**: Version conflicts, bloated trees, slower resolution
- **Solution**: Centralize dev dependencies in workspace root only

### 2. Heavy AI Dependencies  
- **Problem**: `ai-backends` extra pulls torch (~2GB) for all installations
- **Impact**: Most users get unnecessary 2GB+ downloads
- **Solution**: Make AI backends truly optional or separate package

### 3. Mixed Dependency Sources
- **Problem**: Workspace deps + external packages can create conflicts
- **Impact**: Resolution conflicts and version mismatches
- **Solution**: Cleaner separation of concerns

## Recommended Fixes

### Option 1: Workspace-Centric (Recommended)
```toml
# pyproject.toml (root)
[project.optional-dependencies]
dev = ["pytest", "black", "ruff", "mypy", ...]
ai = ["torch", "transformers", ...]  # Heavy deps separate
docs = ["mkdocs", "mkdocs-material", ...]

# packages/lamina-core/pyproject.toml  
[project]
dependencies = ["pydantic", "pyyaml", ...]  # Core only
# NO dev dependencies here
```

### Option 2: Dependency Groups (uv v0.5+)
```toml
[dependency-groups]
dev = ["pytest", "black", "ruff", ...]
ai = ["torch", "transformers", ...]
docs = ["mkdocs", ...]
```

### Option 3: Separate AI Package
```
lamina-core/        # Core framework (lightweight)
lamina-ai/          # AI backends (heavy)  
lamina-llm-serve/   # Model serving
```

## Migration Strategy

1. **Phase 1**: Remove duplicate dev deps from individual packages
2. **Phase 2**: Move AI dependencies to separate optional group
3. **Phase 3**: Consider dependency groups for better organization

## Benefits After Fix

- **Faster installs**: Core users avoid 2GB+ AI dependencies
- **Cleaner resolution**: No duplicate dependency definitions
- **Better caching**: uv can cache more efficiently
- **Easier maintenance**: Single source of truth for dev deps

## Commands After Fix

```bash
# Core development (lightweight)
uv sync --extra dev

# AI development (heavy)  
uv sync --extra dev --extra ai

# Docs only
uv sync --extra docs

# Everything
uv sync --all-extras
```