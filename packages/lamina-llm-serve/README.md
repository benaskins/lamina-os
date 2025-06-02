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
├── models/
│   ├── llama3-70b-q4_k_m/
│   ├── yi-34b-awq/
│   ├── llama3-70b-q5_k_m/
│   └── mistral-7b-instruct/
├── models.yaml
├── scripts/
│   └── fetch-models.py
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

In `lamina-core`, agents reference this manifest indirectly:

* Model-to-agent mapping occurs **within Lamina OS**
* `lamina-llm-serve` is **model aware**, acting as a unified server rather than a simple cache
* Ensures consistent, centralized loading and version control

Example Docker Compose volume mount:

```yaml
volumes:
  - ./lamina-llm-serve/models:/models
```

---

## 🔧 Backends Supported

| Backend     | Format         | Usage                              |
| ----------- | -------------- | ---------------------------------- |
| `llama.cpp` | `.gguf`        | Local CPU or quantized models      |
| `mlc-serve` | AWQ compiled   | Metal-accelerated on Apple Silicon |
| `vllm`      | `.safetensors` | Batch eval, future extensions      |

---

## 🧪 Optional REST API (Planned)

Provides:

* `/models` – list all available
* `/models/:name` – fetch model info
* `/download/:hf_id` – trigger pull
* `/refresh` – reload manifest

---

## 🥐 Setup Instructions

1. Clone this repo:

   ```bash
   git clone https://your-repo-url/lamina-llm-serve.git
   cd lamina-llm-serve
   ```

2. Populate `models/` manually or use the helper script:

   ```bash
   python scripts/fetch-models.py --name llama3-70b-q4_k_m --hf llama3-70b
   ```

3. Reference `models.yaml` from your Lamina OS configuration.

---

## 🛡️ Philosophy

Models are not interchangeable engines—they are **vessels** for vow-bound symbolic presence. This serving layer anchors those vessels with intention, clarity, and breath.

---

## 📜 License

Mozilla Public License 2.0 - see [LICENSE](../../LICENSE) for details.

