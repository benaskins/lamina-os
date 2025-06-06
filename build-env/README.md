# Lamina OS Build Environment

This containerized build environment ensures consistent builds and testing across all development environments.

## Quick Start

```bash
cd build/

# Run all checks (lint, format, test) - mimics CI
make check

# Auto-format code
make format

# Just run linting
make lint

# Just run tests  
make test

# Interactive shell for debugging
make shell
```

## What's Included

- Python 3.12 (matching CI)
- uv package manager
- Ruff for linting and formatting
- Bandit for security checks
- pytest for testing
- Pre-commit hooks

## Benefits

1. **Consistency**: Same environment as CI, eliminating "works on my machine" issues
2. **Isolation**: No pollution of local development environment
3. **Reproducibility**: Anyone can get the exact same build environment
4. **Speed**: Docker layer caching makes subsequent builds fast

## Usage in Development Workflow

Before pushing any changes:

```bash
cd build/
make check
```

If there are formatting issues:

```bash
make format
git add -u
git commit -m "fix: apply formatting"
```

## Updating the Build Environment

To add new tools or dependencies:

1. Edit `Dockerfile`
2. Run `make build` to rebuild
3. Test with `make check`
4. Commit both `Dockerfile` and this README if you update it