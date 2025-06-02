# 🧱 Lamina LLM Serve

**Lamina LLM Serve** is a local-first, centralized model-serving layer for Lamina OS. It manages downloads and runs models so agents share consistent, persistent access—ensuring efficiency and symbolic alignment across the sanctuary.

---

## 🌱 Purpose

`lamina-llm-serve` solves common issues in multi-agent AI environments:

* Prevents redundant downloads of large models
* Offers a unified directory and manifest for all system models
* Supports multiple backends (e.g., `llama.cpp`, `mlc`, `vllm`)
* Keeps model configuration cleanly decoupled from agent implementation

It serves as the **source of truth** for all LLM usage across `lamina-core`.

---

## 🤩 Directory Structure

```
lamina-llm-serve/
├── lamina_llm_serve/
│   ├── __init__.py
│   ├── model_manager.py    # Model discovery and validation
│   ├── backends.py         # Backend abstraction layer
│   ├── downloader.py       # Multi-source model downloads
│   └── server.py          # HTTP REST API server
├── models/                 # Downloaded models (gitignored)
├── scripts/
│   └── model-manager.py   # CLI tool for model operations
├── models.yaml            # Model manifest
└── README.md
```

---

## 🎞️ Model Manifest (`models.yaml`)

Each model is described with its local path and associated runtime backend:

```yaml
models:
  llama3-70b-q4_k_m:
    path: /models/llama3-70b-q4_k_m/model.gguf
    backend: llama.cpp
  yi-34b-awq:
    path: /models/yi-34b-awq/
    backend: mlc
  llama3-70b-q5_k_m:
    path: /models/llama3-70b-q5_k_m/
    backend: llama.cpp
  mistral-7b-instruct:
    path: /models/mistral-7b-instruct/
    backend: llama.cpp
```

---

## 💠 Usage Within Lamina OS

In `lamina-core`, agents reference models through this service:

* Model-to-agent mapping occurs **within Lamina OS**
* `lamina-llm-serve` is **model aware**, acting as a unified server rather than a simple cache
* Ensures consistent, centralized loading and version control

Example usage:

```python
from lamina_llm_serve import ModelManager

manager = ModelManager()
models = manager.list_models()
print(f"Available models: {models}")
```

---

## 🔧 Backends Supported

| Backend     | Format         | Usage                              |
| ----------- | -------------- | ---------------------------------- |
| `llama.cpp` | `.gguf`        | Local CPU or quantized models      |
| `mlc-serve` | AWQ compiled   | Metal-accelerated on Apple Silicon |
| `vllm`      | `.safetensors` | Batch eval, future extensions      |

---

## 🧪 REST API

The included HTTP server provides:

* `GET /models` – List all available models
* `GET /models/<name>` – Get specific model info
* `GET /backends` – List available backends
* `POST /download` – Download a model
* `GET /health` – Server health check

Start the server:
```bash
python -m lamina_llm_serve.server --port 8000
```

---

## 🥐 Setup Instructions

1. Install the package:

   ```bash
   pip install lamina-llm-serve
   ```

2. Download models using the CLI:

   ```bash
   # List available models for download
   python scripts/model-manager.py list-downloadable
   
   # Download a specific model
   python scripts/model-manager.py download llama3.2-1b-q4_k_m --source huggingface
   ```

3. Validate your setup:

   ```bash
   python scripts/model-manager.py validate
   ```

---

## 🛡️ Philosophy

Models are not interchangeable engines—they are **vessels** for vow-bound symbolic presence. This serving layer anchors those vessels with intention, clarity, and breath.

---

## 📜 License

Mozilla Public License 2.0 - see [LICENSE](../../LICENSE) for details.