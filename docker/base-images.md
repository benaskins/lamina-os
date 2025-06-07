# Lamina OS Base Image Standards

## Security Requirements

All Docker base images MUST:
1. Use specific digests (not tags) for reproducibility
2. Minimize attack surface with Alpine when possible
3. Run as non-root user
4. Include security updates

## Approved Base Images

### Python Applications
```dockerfile
# RECOMMENDED: Alpine-based Python (smallest, most secure)
FROM python:3.12-alpine3.19@sha256:c7eb5c92b7933b7a4e0c0d3ad6140548b2389cac49f6437a4d026e70764a8611

# ALTERNATIVE: Slim if Alpine incompatible (some C extensions)
FROM python:3.12-slim-bookworm@sha256:xyz...
```

### Infrastructure Services
```dockerfile
# Vector (logging)
FROM timberio/vector:0.34.0-alpine@sha256:abc...

# Nginx (proxy)
FROM nginx:1.25-alpine@sha256:def...
```

## Security Hardening Template

```dockerfile
# Use specific digest
FROM python:3.12-alpine@sha256:specific-digest-here

# Install security updates
RUN apk update && apk upgrade && rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -g 1001 -S lamina && \
    adduser -u 1001 -S lamina -G lamina

# Install dependencies as root
RUN apk add --no-cache git make

# Switch to non-root user
USER lamina
WORKDIR /home/lamina

# Copy and install Python deps
COPY --chown=lamina:lamina requirements.txt .
RUN pip install --user -r requirements.txt

# Copy application
COPY --chown=lamina:lamina . .

# Run as non-root
CMD ["python", "app.py"]
```

## Migration Plan

1. Update build-env/Dockerfile to Alpine + non-root
2. Standardize all Python containers to 3.12
3. Pin all image digests
4. Add security scanning to CI