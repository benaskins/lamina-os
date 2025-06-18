# Lamina Dashboard Container
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl for Kubernetes access
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/

# Install uv for fast dependency management
RUN pip install uv

# Create non-root user
RUN groupadd -r lamina && useradd -r -g lamina -u 1000 lamina

# Set working directory
WORKDIR /app

# Copy package files
COPY pyproject.toml ./
COPY gunicorn.conf.py ./
COPY config/ ./config/
COPY lamina_dashboard/ ./lamina_dashboard/
COPY static/ ./static/
COPY templates/ ./templates/
COPY requirements.txt ./

# Create README for container context
RUN echo "# Lamina Dashboard Docker Container" > README.md

# Install dependencies
RUN uv sync

# Create home directory and cache for lamina user
RUN mkdir -p /home/lamina/.cache && \
    chown -R lamina:lamina /app /home/lamina

# Switch to non-root user
USER lamina

# Set home directory
ENV HOME=/home/lamina

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/api/cluster/state || exit 1

# Run the dashboard
CMD ["uv", "run", "lamina-dashboard"]