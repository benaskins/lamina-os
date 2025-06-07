# Lamina OS Build Environment
# Ensures consistent builds across all environments

FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install uv for Python package management
RUN pip install uv

# Verify uv is available
RUN uv --version

# Set working directory
WORKDIR /workspace

# Copy project files
COPY pyproject.toml uv.lock ./
COPY packages/ ./packages/

# Install all dependencies including dev tools
RUN uv sync --all-extras

# Default command runs all checks
CMD ["make", "check"]