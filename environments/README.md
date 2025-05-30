# Environment Configurations

This directory contains environment-specific configurations for Lamina OS's three-tier architecture.

## Structure

```
environments/
├── development/
│   └── config.yaml      # 🜂 Development environment
├── test/
│   └── config.yaml      # 🜁 Test environment  
├── production/
│   └── config.yaml      # 🜄 Production environment
└── README.md           # This file
```

## Usage

These configurations are loaded by the `lamina.environment` module:

```python
from lamina.environment import EnvironmentManager

manager = EnvironmentManager()
config = manager.get_environment_config("development")
print(f"{config.sigil} Environment: {config.name}")
```

## Environment Types

- **🜂 Development**: Docker Compose, hot-reload, debugging
- **🜁 Test**: Containerized, ephemeral, CI/CD integration
- **🜄 Production**: Kubernetes, auto-scaling, comprehensive monitoring

## Validation

All configurations are validated for:
- Sigil consistency across services
- Security requirements per environment
- Resource allocation appropriateness
- Service dependency completeness

See the [Environment Documentation](../docs/environments/) for detailed usage instructions.