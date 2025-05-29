# Claude Code Documentation - lamina_llm_serve Package

## Package Architecture

This package implements the core model serving infrastructure with clear separation of concerns:

### Core Components

**model_manager.py**
- Central registry for all model metadata
- Validates model availability on filesystem
- Provides model suggestions based on use cases
- Loads and parses models.yaml manifest

**backends.py**
- Abstract base class for LLM serving engines
- Concrete implementations for llama.cpp, MLC-serve, vLLM
- Backend availability detection and validation
- Unified interface for model server lifecycle

**downloader.py**
- Multi-source model downloading capabilities
- Progress tracking for large model downloads
- Integration with ModelManager for manifest updates
- Support for HuggingFace, Ollama, URLs, local files

**server.py**
- Flask-based HTTP REST API
- Model discovery and status endpoints
- Backend information and validation
- Model server lifecycle management
- Chat proxy for active model sessions

## Key Classes

### ModelManager
```python
# Primary interface for model operations
manager = ModelManager("models.yaml", "models/")
models = manager.list_models()
available = manager.validate_models()
suggested = manager.suggest_model({"use_case": "conversational"})
```

### LLMBackend (Abstract)
```python
# Backend implementation pattern
class CustomBackend(LLMBackend):
    def is_available(self) -> bool:
        # Check if backend executable exists
    
    def start_model(self, model_path: str, **kwargs) -> bool:
        # Start model server process
    
    def stop_model(self, model_name: str) -> bool:
        # Stop model server process
```

### ModelDownloader
```python
# Download models from various sources
downloader = ModelDownloader("models/", manifest_data)
success = downloader.download_model("model-name", config)
downloadable = downloader.list_downloadable_models()
```

## Import Patterns

```python
# Standard imports for this package
from lamina_llm_serve.model_manager import ModelManager
from lamina_llm_serve.backends import LlamaCppBackend, MLCBackend, VLLMBackend
from lamina_llm_serve.downloader import ModelDownloader
from lamina_llm_serve.server import create_app
```

## Error Handling

- Use logging extensively for debugging model operations
- Graceful degradation when backends are unavailable
- Clear error messages for missing models or failed downloads
- Validate manifest data before processing

## Configuration Patterns

Models should define complete backend configurations:
```yaml
model-name:
  path: relative/path/to/model.gguf
  backend: llama.cpp
  size: "2.0GB"
  description: "Model description"
  download:
    huggingface:
      repo_id: "org/model-name"
      filename: "model.gguf"
```

## Testing Notes

- ModelManager operations require valid models.yaml
- Backend tests should check for executable availability
- Download tests may require network access
- Server tests should use test client, not live HTTP calls

## Performance Considerations

- Model validation can be expensive for large collections
- Cache backend availability checks
- Use streaming for large model downloads
- Lazy load model metadata when possible