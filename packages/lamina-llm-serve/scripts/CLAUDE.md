# Luthier Documentation - Scripts Directory

## CLI Tools Overview

This directory contains command-line interfaces for lamina-llm-serve operations.

### model-manager.py

The primary CLI tool for all model management operations. Provides a rich command interface with comprehensive help and status indicators.

#### Command Structure

**CRITICAL**: Always use `uv run` for Python commands in this workspace.

```bash
# Environment setup (always first)
cd packages/lamina-llm-serve
uv sync

# Run CLI tool
uv run python scripts/model-manager.py [global-options] <command> [command-options]
```

#### Global Options
- `--manifest MANIFEST`: Path to model manifest (default: models.yaml)
- `--models-dir MODELS_DIR`: Path to models directory (default: models)
- `--verbose, -v`: Enable verbose output

#### Available Commands

**Model Information**
```bash
uv run python scripts/model-manager.py list                    # List all models with status indicators
uv run python scripts/model-manager.py validate               # Validate model availability
uv run python scripts/model-manager.py info <model-name>      # Detailed model information
uv run python scripts/model-manager.py stats                  # Collection statistics
```

**Backend Operations**
```bash
uv run python scripts/model-manager.py backends               # Check backend availability and versions
```

**Model Discovery**
```bash
uv run python scripts/model-manager.py suggest                # Suggest models based on requirements
  --use-case <case>    # Filter by use case (conversational, analytical, etc.)
  --category <cat>     # Filter by category (lightweight, balanced, reasoning)
```

**Download Operations**
```bash
uv run python scripts/model-manager.py list-downloadable      # List all downloadable models
  --source <source>    # Filter by source (huggingface, ollama)

uv run python scripts/model-manager.py download <model>       # Download a specific model
  --source <source>    # Specify download source

uv run python scripts/model-manager.py install <model> <path> # Install model from local path
```

## Implementation Patterns

### Command Function Structure
```python
def cmd_operation_name(manager: ModelManager, args):
    """Command description"""
    # 1. Extract arguments
    # 2. Perform operation using manager
    # 3. Format and display results
    # 4. Handle errors gracefully
```

### Error Handling
- Use try/catch for all operations
- Display user-friendly error messages
- Exit with appropriate status codes
- Log detailed errors for debugging

### Output Formatting
- Use emoji and symbols for status indicators
- Consistent formatting across commands
- Verbose mode for detailed information
- Progress indicators for long operations

### Integration with Core Package
```python
# Standard initialization pattern
try:
    manager = ModelManager(args.manifest, args.models_dir)
except Exception as e:
    logger.error(f"Failed to initialize model manager: {e}")
    sys.exit(1)

# Pass manager to command functions
args.func(manager, args)
```

## Adding New Commands

1. **Create command function**:
   ```python
   def cmd_new_operation(manager: ModelManager, args):
       """Description of new operation"""
       # Implementation
   ```

2. **Add argument parser**:
   ```python
   new_parser = subparsers.add_parser('new-operation', help='Description')
   new_parser.add_argument('--option', help='Option description')
   new_parser.set_defaults(func=cmd_new_operation)
   ```

3. **Test with various scenarios**:
   - Valid inputs
   - Invalid/missing models
   - Backend unavailability
   - Network issues (for downloads)

4. **Verify with containerized CI** (MANDATORY):
   ```bash
   # From project root - ALWAYS run before pushing
   ./scripts/check-build.sh
   ```
   
   **PIR Lesson**: Never assume CLI changes work without containerized verification.

## CLI Design Principles

- **Consistent**: Same patterns across all commands
- **Informative**: Clear status indicators and progress
- **Robust**: Handle missing dependencies gracefully
- **Scriptable**: Support for automation and scripting
- **Interactive**: Rich output for human users

## Dependencies Integration

The CLI scripts should gracefully handle missing optional dependencies:

```python
# Example pattern for optional imports
try:
    from lamina_llm_serve.downloader import ModelDownloader
    DOWNLOAD_AVAILABLE = True
except ImportError:
    DOWNLOAD_AVAILABLE = False
    
# Then check before using
if not DOWNLOAD_AVAILABLE:
    print("❌ Download functionality requires additional dependencies")
    print("   Run: pip install tqdm huggingface_hub")
    sys.exit(1)
```