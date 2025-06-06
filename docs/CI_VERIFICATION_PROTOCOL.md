# CI Verification Protocol

Based on lessons learned from PIR-2025-01-06 (Ruff Linting CI Failures), this document establishes the required verification steps before pushing changes.

## Required Steps Before Pushing

### 1. Use Containerized Build Environment (Recommended)
The easiest way to ensure your code will pass CI:

```bash
# From project root
./scripts/check-build.sh

# Or from build-env directory
cd build-env/
make check
```

This runs exactly the same checks as CI in a containerized environment.

### 2. Manual Local CI Simulation (Alternative)
If you can't use Docker, run these commands locally:

```bash
# Run the exact same linting tools as CI
uv run ruff check
uv run ruff format --check

# Run tests
uv run pytest packages/lamina-core/tests/ -x
```

### 3. Configuration Verification
Ensure your local tools match CI configuration:
- Check `.github/workflows/ci.yml` for the exact commands
- Verify tool versions match between local and CI environments
- Confirm all packages are using the same linter configuration

### 4. After Pushing
- Monitor the PR checks on GitHub
- If CI fails, check the logs immediately
- Fix any issues before proceeding with other work

## Common Issues and Solutions

### Linting Tool Mismatch
**Problem**: Local uses different linter than CI
**Solution**: Always check `.github/workflows/ci.yml` for current tools

### Import Errors
**Problem**: Imports work locally but fail in CI
**Solution**: Test with clean environment using `uv sync`

### Format Differences
**Problem**: Local formatting differs from CI
**Solution**: Use exact same formatter version and settings as CI

## Integration with Development Workflow

This protocol should be followed for EVERY commit that will be pushed:
1. Make changes
2. Run local CI simulation
3. Fix any issues
4. Commit with confidence
5. Push and verify

Remember: The goal is to catch issues locally before they reach CI, saving time and maintaining a clean commit history.