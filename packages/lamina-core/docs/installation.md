# Installation Guide

## Requirements

- Python 3.11 or higher
- 4GB+ RAM recommended
- Docker (optional, for containerized deployment)

## Installation

### From PyPI (when published)

```bash
pip install lamina-core
```

### From Source

```bash
git clone <repository-url>
cd lamina-core
pip install -e .
```

### Development Installation

```bash
git clone <repository-url>
cd lamina-core
pip install -r requirements-dev.txt
pip install -e .
```

## Quick Start

1. **Create your first sanctuary:**

```bash
lamina sanctuary init my-agents
cd my-agents
```

2. **Create an agent:**

```bash
lamina agent create assistant --template=conversational
```

3. **Try the chat demo:**

```bash
lamina chat --demo
```

4. **Generate infrastructure (coming soon):**

```bash
lamina infrastructure generate
```

## AI Backend Setup

### Ollama (Recommended)

Install Ollama for local AI models:

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.2:3b
```

### HuggingFace

For HuggingFace models:

```bash
pip install transformers torch
```

## Docker Setup (Optional)

For containerized deployment:

```bash
# Build containers
lamina docker build

# Start services
lamina docker up
```

## Verification

Test your magical installation:

```bash
python -c "import lamina; print(f'Lamina Core v{lamina.__version__} - Ready to make magic!')"
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure all dependencies are installed
2. **Memory issues**: Use smaller models for limited RAM
3. **Docker issues**: Ensure Docker is running and accessible

### Getting Help

- Check the documentation: `docs/`
- Run with verbose output: `lamina --verbose <command>`
- Report issues: [GitHub Issues](https://github.com/benaskins/lamina-os/issues)