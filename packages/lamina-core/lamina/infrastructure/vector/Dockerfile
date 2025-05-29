FROM timberio/vector:0.34.0-alpine

# Create directory for Vector data
RUN mkdir -p /vector-data-dir

# Copy our configuration
COPY vector.toml /etc/vector/vector.toml

# Expose Vector's API port (optional, for monitoring)
EXPOSE 8686

CMD ["--config", "/etc/vector/vector.toml"]
