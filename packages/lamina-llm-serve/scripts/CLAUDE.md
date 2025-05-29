# Claude Code Documentation - Scripts Directory

## CLI Tools Overview

This directory contains command-line interfaces for lamina-llm-serve operations.

### model-manager.py

The primary CLI tool for all model management operations. Provides a rich command interface with comprehensive help and status indicators.

#### Command Structure

```bash
python scripts/model-manager.py [global-options] <command> [command-options]
```

#### Global Options
- `--manifest MANIFEST`: Path to model manifest (default: models.yaml)
- `--models-dir MODELS_DIR`: Path to models directory (default: models)
- `--verbose, -v`: Enable verbose output

#### Available Commands

**Model Information**
```bash
list                    # List all models with status indicators
validate               # Validate model availability
info <model-name>      # Detailed model information
stats                  # Collection statistics
```

**Backend Operations**
```bash
backends               # Check backend availability and versions
```

**Model Discovery**
```bash
suggest                # Suggest models based on requirements
  --use-case <case>    # Filter by use case (conversational, analytical, etc.)
  --category <cat>     # Filter by category (lightweight, balanced, reasoning)
```

**Download Operations**
```bash
list-downloadable      # List all downloadable models
  --source <source>    # Filter by source (huggingface, ollama)

download <model>       # Download a specific model
  --source <source>    # Specify download source

install <model> <path> # Install model from local path
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