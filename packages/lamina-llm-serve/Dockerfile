# Dockerfile for lamina-llm-serve testing
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install uv for faster dependency management
RUN pip install uv

# Create non-root user
RUN groupadd -r lamina && useradd -r -g lamina -u 1000 lamina

# Set working directory
WORKDIR /app

# Copy project files
COPY pyproject.toml ./
COPY lamina_llm_serve/ ./lamina_llm_serve/
COPY scripts/ ./scripts/
COPY models.yaml ./

# Create a minimal README for build
RUN echo "# lamina-llm-serve Docker container" > README.md

# Install dependencies as root, then fix permissions
RUN uv sync

# Create models directory and set permissions
RUN mkdir -p models

# Change ownership of entire /app directory to lamina user
RUN chown -R lamina:lamina /app

# Switch to non-root user
USER lamina

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uv", "run", "python", "-m", "lamina_llm_serve.server", "--host", "0.0.0.0", "--port", "8000"]