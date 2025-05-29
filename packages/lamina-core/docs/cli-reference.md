# CLI Reference

Complete reference for all `lamina` commands in the magical symbolic operating system.

## Global Commands

```bash
lamina --help              # Show help
lamina --version           # Show version
lamina --verbose           # Enable verbose output
```

## Sanctuary Management

### Create Sanctuary
```bash
lamina sanctuary init <name>                    # Interactive creation
lamina sanctuary init <name> --non-interactive  # Use defaults
lamina sanctuary init <name> --template=advanced # Use template
```

### Sanctuary Operations
```bash
lamina sanctuary list       # List sanctuaries in current directory
lamina sanctuary status     # Show current sanctuary status
lamina sanctuary status --path=/path/to/sanctuary  # Check specific sanctuary
```

## Agent Management

### Create Agents
```bash
lamina agent create <name>                       # Default conversational agent
lamina agent create <name> --template=analytical # Research specialist
lamina agent create <name> --template=security   # Security specialist  
lamina agent create <name> --template=reasoning  # Logic specialist
lamina agent create <name> --provider=huggingface # Use HuggingFace backend
lamina agent create <name> --model=llama3.2:7b   # Specify model
```

### Agent Operations
```bash
lamina agent list           # List agents in current sanctuary
lamina agent info <name>    # Show agent details
```

## Chat Interface

### Demo Chat (No Sanctuary Required)
```bash
lamina chat --demo                              # Interactive demo
lamina chat --demo "Hello, analyze this data"  # Single message demo
```

### Sanctuary Chat (Future)
```bash
lamina chat                 # Interactive chat with coordinator
lamina chat <agent>         # Chat with specific agent
lamina chat <agent> "msg"   # Send single message
```

## Infrastructure Management

### Generate Infrastructure
```bash
lamina infrastructure generate                  # Generate for all agents
lamina infrastructure generate --agent=<name>  # Generate for specific agent
lamina infrastructure status                   # Show infrastructure status
```

## Docker Operations

### Container Management
```bash
lamina docker build         # Build all containers
lamina docker up            # Start all services
lamina docker down          # Stop all services
lamina docker logs          # Show container logs
lamina docker status        # Show container status
```

## Complete Workflow Examples

### Basic Setup
```bash
# Create sanctuary
lamina sanctuary init my-ai-system

# Navigate to sanctuary
cd my-ai-system

# Create agents
lamina agent create assistant --template=conversational
lamina agent create researcher --template=analytical
lamina agent create guardian --template=security

# Check status
lamina sanctuary status
lamina agent list

# Try chat demo
lamina chat --demo "Hello, I need help analyzing security logs"
```

### Advanced Setup
```bash
# Create advanced sanctuary
lamina sanctuary init enterprise-ai --template=advanced

cd enterprise-ai

# Create specialized agents
lamina agent create customer-service --template=conversational
lamina agent create data-analyst --template=analytical --model=llama3.2:7b
lamina agent create security-monitor --template=security
lamina agent create problem-solver --template=reasoning

# Generate infrastructure
lamina infrastructure generate

# Build and deploy
lamina docker build
lamina docker up

# Check deployment
lamina docker status
lamina sanctuary status
```

### Development Workflow
```bash
# Quick development setup
lamina sanctuary init dev-test --non-interactive
cd dev-test

# Create and test agent
lamina agent create test-agent
lamina chat --demo "Test message"

# Check configuration
lamina agent info test-agent
lamina sanctuary status
```

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: Command not found
- `3`: Invalid arguments
- `4`: Not in sanctuary (when required)

## Environment Variables

- `LAMINA_VERBOSE`: Enable verbose output (set to any value)
- `LAMINA_CONFIG_PATH`: Override default config path
- `LAMINA_AI_PROVIDER`: Default AI provider (ollama, huggingface)
- `LAMINA_AI_MODEL`: Default AI model

## Configuration Files

### Sanctuary Structure
```
my-sanctuary/
├── lamina.yaml                 # Project configuration
├── config/
│   ├── system.yaml            # System configuration
│   └── infrastructure.yaml    # Infrastructure settings
├── sanctuary/
│   ├── agents/               # Agent definitions
│   ├── system/              # System-level configs
│   └── vows/                # Constraint definitions
└── infrastructure/           # Generated infrastructure files
```

### Agent Structure
```
agents/<name>/
├── agent.yaml              # Agent configuration
├── infrastructure.yaml     # Infrastructure settings
├── known_entities.yaml     # Entity definitions
└── ollama/Modelfile        # Model configuration (if using Ollama)
```

## Tips

1. **Always run commands from sanctuary directory** for agent/infrastructure operations
2. **Use `--demo` flag** to test chat functionality without setting up full infrastructure  
3. **Check status frequently** with `lamina sanctuary status` and `lamina agent list`
4. **Use templates** to get started quickly with specialized agent types
5. **Use `--verbose`** flag when debugging issues