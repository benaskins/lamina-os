# Testing Guide - Lamina OS

This document covers testing procedures for the Lamina OS framework.

## Overview

Lamina OS uses a comprehensive testing approach that includes:
- Unit tests with pytest
- Integration tests for multi-package workflows
- Real LLM comprehension testing for sigil validation
- Security scanning with bandit
- Type checking with mypy

## Standard Testing

### Quick Tests
```bash
# Run basic unit tests
uv run pytest

# Run with coverage
uv run pytest --cov=packages --cov-report=term-missing

# Fast tests only (skip slow integration tests)
uv run pytest -m "not slow"
```

### Full Test Suite
```bash
# Run all tests including integration
uv run pytest --cov=packages --cov-report=xml

# Code quality checks
uv run ruff check
uv run black --check .
uv run mypy packages/
uv run bandit -r packages/
```

## Real LLM Comprehension Testing

The sigil script system includes validation using a real containerized LLM to ensure symbolic notation maintains comprehension accuracy.

### Prerequisites
- Docker installed and running
- ~3GB disk space for LLM model
- Network access for model download

### Running LLM Tests

```bash
# Install test dependencies
uv sync --extra test-llm

# Run comprehensive sigil comprehension test
uv run python tools/test-sigil-comprehension.py
```

### What the LLM Test Does

1. **Starts containerized Ollama** with phi3:mini model (~2.3GB)
2. **Tests real comprehension** by asking the LLM questions about both traditional and sigil versions of documentation
3. **Measures token reduction** while validating comprehension retention
4. **Provides detailed analysis** of concept coverage and accuracy

### LLM Test Process

```
🧪 Real LLM Sigil Comprehension Testing
==================================================
🚀 Starting test LLM container...
📥 Pulling lightweight test model (phi3:mini)...
✅ Test LLM started successfully
🔍 Testing LLM connectivity...
✅ LLM is responding: Hello! Yes, I can respond...

📁 Testing Aurelia CLAUDE.md files with real LLM
🧪 Testing: What Python environment manager must be used?
  📝 Querying traditional format...
  📝 Querying sigil format...
  Traditional score: 0.75 (found: ['uv', 'required'])
  Sigil score: 0.75 (found: ['uv', 'required'])
  Relative comprehension: 1.00
  ...

📊 FINAL ANALYSIS (Real LLM Testing)
==================================================
✅ Success Rate: 83.3%
🧠 Avg Comprehension Retention: 89.2%
📉 Avg Token Reduction: 67.1%
```

### Managing Test LLM

```bash
# Manual container management
./tools/setup-test-llm.sh          # Start LLM container
./tools/cleanup-test-llm.sh        # Stop and cleanup

# Check if running
docker ps | grep lamina-test-llm

# View logs
docker logs lamina-test-llm
```

### Test Configuration

The LLM test uses:
- **Model**: phi3:mini (2.3GB, Microsoft's lightweight model)
- **Port**: 11435 (to avoid conflicts with main Ollama)
- **Temperature**: 0.1 (for consistent results)
- **Response limit**: 200 tokens

### Success Criteria

- **Success Rate**: ≥70% of tests pass comprehension validation
- **Comprehension Retention**: ≥70% average concept coverage
- **Token Reduction**: ≥50% reduction vs traditional format

### Troubleshooting

**Container Won't Start:**
```bash
# Check Docker is running
docker ps

# Check port availability
lsof -i :11435

# Manual cleanup
docker stop lamina-test-llm
docker rm lamina-test-llm
```

**Model Download Issues:**
```bash
# Check network and disk space
df -h
ping ollama.ai

# Manual model pull
docker exec lamina-test-llm ollama pull phi3:mini
```

**Test Failures:**
- Review detailed JSON results file for specific comprehension failures
- Consider updating expected concepts for new documentation
- Verify sigil script maintains semantic equivalence

## Continuous Integration

GitHub Actions runs:
- Standard test suite on Python 3.11, 3.12, 3.13
- Package isolation tests
- Security and type checking
- Build validation

LLM comprehension tests run manually due to resource requirements and model download size.

## Test Data

Test results are saved with timestamps:
- `sigil_comprehension_test_results_real_llm_{timestamp}.json`
- Contains detailed LLM responses and concept analysis
- Used for validation documentation and improvement

---

*Real LLM testing ensures our sigil system genuinely maintains AI comprehension, not just keyword matching.*