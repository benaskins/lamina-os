FROM chromadb/chroma:latest

# Install additional packages for mTLS support
USER root
RUN apt-get update && apt-get install -y \
    curl \
    openssl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create chromadb user and directories
RUN groupadd -r chromadb && useradd -r -g chromadb chromadb

# Create data and certificate directories
RUN mkdir -p /chroma/data /chroma/certs && \
    chown -R chromadb:chromadb /chroma

# Copy configuration
COPY chroma-config.yaml /chroma/config.yaml

# Set proper permissions
RUN chown chromadb:chromadb /chroma/config.yaml

# Switch to chromadb user
USER chromadb

# Set environment variables
ENV CHROMA_SERVER_HOST=0.0.0.0
ENV CHROMA_SERVER_HTTP_PORT=8000
ENV CHROMA_SERVER_CORS_ALLOW_ORIGINS=["*"]
ENV CHROMA_SERVER_AUTH_CREDENTIALS_PROVIDER=chromadb.auth.token.TokenAuthCredentialsProvider
ENV CHROMA_SERVER_AUTH_CREDENTIALS=lamina_chroma_token
ENV CHROMA_SERVER_AUTH_PROVIDER=chromadb.auth.token.TokenAuthServerProvider

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v2/heartbeat || exit 1

# Expose port
EXPOSE 8000

# Start ChromaDB
CMD ["run", "--host", "0.0.0.0", "--port", "8000", "--path", "/chroma/data"] 