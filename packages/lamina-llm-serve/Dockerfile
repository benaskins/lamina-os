# Dockerfile for lamina-llm-serve testing
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY lamina_llm_serve/ ./lamina_llm_serve/
COPY scripts/ ./scripts/
COPY models.yaml ./

# Create a minimal README for build
RUN echo "# lamina-llm-serve Docker container" > README.md

# Install dependencies (skip frozen lock for now)
RUN uv sync

# Create models directory
RUN mkdir -p models

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uv", "run", "python", "-m", "lamina_llm_serve.server", "--host", "0.0.0.0", "--port", "8000"]