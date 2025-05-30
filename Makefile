# Lamina OS Test Management - ADR-0010 Implementation
# CLI shortcuts per Ansel's suggestion for test tier management

.PHONY: help test test-unit test-integration test-e2e test-all test-watch test-coverage clean-artifacts setup-test-env

# Default target
help:
	@echo "🧪 Lamina OS Testing - ADR-0010 Test Tiers"
	@echo ""
	@echo "Test Commands:"
	@echo "  test          Run unit tests only (default, fast)"
	@echo "  test-unit     Run unit tests explicitly"  
	@echo "  test-integration  Run integration tests with Docker containers"
	@echo "  test-integration-local  Run integration tests locally (fallback)"
	@echo "  test-e2e      Run end-to-end tests (full system)"
	@echo "  test-all      Run all test tiers (unit + integration + e2e)"
	@echo "  test-watch    Run unit tests in watch mode"
	@echo "  test-coverage Generate test coverage report"
	@echo ""
	@echo "Test Infrastructure:"
	@echo "  setup-test-env    Set up test environment and LLM server"
	@echo "  clean-artifacts   Clean test artifacts and logs"
	@echo ""
	@echo "Examples:"
	@echo "  make test                    # Fast unit tests for development"
	@echo "  make test-integration        # Test with real AI models"
	@echo "  make test-all                # Complete test validation"

# Unit Tests (Fast, Default)
test: test-unit

test-unit:
	@echo "🏃‍♂️ Running Unit Tests (Fast)"
	@echo "Testing: API contracts, mocks, edge cases"
	@echo "Expected duration: < 30 seconds"
	@echo ""
	uv run pytest packages/lamina-core/tests/ -v --tb=short -x
	@echo ""
	@echo "✅ Unit tests completed"

# Integration Tests (Real AI Models)
test-integration:
	@echo "🤖 Running Integration Tests (Real AI Models)"
	@echo "Testing: Real backends, actual model responses, quality metrics"
	@echo "Expected duration: 1-5 minutes"
	@echo "Using: Docker containers for isolated testing"
	@echo ""
	@echo "🐳 Starting containerized test environment..."
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
	@echo ""
	@echo "✅ Integration tests completed"

# Integration Tests (Local mode - fallback)
test-integration-local:
	@echo "🤖 Running Integration Tests (Local Mode)"
	@echo "Testing: Real backends, actual model responses, quality metrics"
	@echo "Expected duration: 1-5 minutes"
	@echo "Requires: lamina-llm-serve running with llama3.2-1b-q4_k_m"
	@echo ""
	@if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "❌ LLM server not detected at http://localhost:8000"; \
		echo "Please start lamina-llm-serve:"; \
		echo "  cd packages/lamina-llm-serve && uv run python -m lamina_llm_serve.server"; \
		exit 1; \
	fi
	@echo "✅ LLM server detected, running integration tests..."
	uv run pytest packages/lamina-core/tests/ --integration -v --tb=short
	@echo ""
	@echo "✅ Integration tests completed"

# E2E Tests (Full System)
test-e2e:
	@echo "🌍 Running End-to-End Tests (Full System)"
	@echo "Testing: Complete workflows, multi-agent collaboration, performance"
	@echo "Expected duration: 5-30 minutes"
	@echo ""
	@if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "❌ LLM server not detected at http://localhost:8000"; \
		exit 1; \
	fi
	uv run pytest packages/lamina-core/tests/ --e2e -v --tb=short
	@echo ""
	@echo "✅ E2E tests completed"

# All Tests (Complete Validation)
test-all:
	@echo "🎯 Running All Test Tiers (Complete Validation)"
	@echo "This will run: Unit → Integration → E2E tests"
	@echo "Expected duration: 5-35 minutes total"
	@echo ""
	@$(MAKE) test-unit
	@echo ""
	@$(MAKE) test-integration
	@echo ""
	@$(MAKE) test-e2e
	@echo ""
	@echo "🎉 All test tiers completed successfully!"

# Watch Mode (Development)
test-watch:
	@echo "👀 Running Unit Tests in Watch Mode"
	@echo "Tests will re-run automatically when files change"
	@echo "Press Ctrl+C to stop"
	@echo ""
	uv run pytest packages/lamina-core/tests/ -v --tb=short -f

# Coverage Report
test-coverage:
	@echo "📊 Generating Test Coverage Report"
	@echo ""
	uv run pytest packages/lamina-core/tests/ --cov=packages --cov-report=html --cov-report=term
	@echo ""
	@echo "✅ Coverage report generated in htmlcov/"
	@echo "Open htmlcov/index.html in browser to view detailed report"

# Test Infrastructure Setup
setup-test-env:
	@echo "🏗️  Setting Up Test Environment"
	@echo ""
	@echo "1. Installing test dependencies..."
	uv sync --extra dev
	@echo ""
	@echo "2. Creating test artifacts directory..."
	mkdir -p packages/lamina-core/test_artifacts
	@echo ""
	@echo "3. Setting up lamina-llm-serve..."
	@if [ -d "../lamina-llm-serve" ]; then \
		echo "✅ lamina-llm-serve found"; \
		cd ../lamina-llm-serve && uv sync; \
		echo "Downloading test model..."; \
		cd ../lamina-llm-serve && uv run python scripts/model-manager.py download llama3.2-1b-q4_k_m --source huggingface || echo "Model download may have failed"; \
		echo "Validating models..."; \
		cd ../lamina-llm-serve && uv run python scripts/model-manager.py validate; \
	else \
		echo "⚠️  lamina-llm-serve not found in ../lamina-llm-serve"; \
		echo "Please ensure lamina-llm-serve is available for integration tests"; \
	fi
	@echo ""
	@echo "4. Test environment setup complete!"
	@echo ""
	@echo "To run integration tests, start LLM server:"
	@echo "  cd ../lamina-llm-serve && uv run python -m lamina_llm_serve.server"

# Clean Test Artifacts
clean-artifacts:
	@echo "🧹 Cleaning Test Artifacts"
	@rm -rf packages/lamina-core/test_artifacts/
	@rm -rf packages/lamina-core/.pytest_cache/
	@rm -rf packages/lamina-core/htmlcov/
	@rm -rf packages/lamina-core/.coverage
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Test artifacts cleaned"

# Development Workflow Shortcuts
dev-test: test-unit
	@echo "💻 Development test cycle complete"

ci-test: test-all
	@echo "🚀 CI test cycle complete"

# Quality Gates
check-quality:
	@echo "🔍 Running Quality Checks"
	@echo ""
	@echo "Linting..."
	uv run ruff check packages/lamina-core/
	@echo ""
	@echo "Formatting..."
	uv run black --check packages/lamina-core/
	@echo ""
	@echo "Type checking..."
	uv run mypy packages/lamina-core/ || echo "⚠️  Type checking issues found"
	@echo ""
	@echo "Security scanning..."
	uv run bandit -r packages/lamina-core/ || echo "⚠️  Security issues found"
	@echo ""
	@echo "✅ Quality checks completed"

# Test Status
test-status:
	@echo "📈 Test Environment Status"
	@echo ""
	@echo "Python Environment:"
	@uv run python --version
	@echo ""
	@echo "Test Dependencies:"
	@uv run python -c "import pytest; print(f'pytest: {pytest.__version__}')" 2>/dev/null || echo "❌ pytest not available"
	@echo ""
	@echo "LLM Server Status:"
	@if curl -s http://localhost:8000/health > /dev/null 2>&1; then \
		echo "✅ LLM server running at http://localhost:8000"; \
		curl -s http://localhost:8000/health | head -n 5; \
	else \
		echo "❌ LLM server not running at http://localhost:8000"; \
	fi
	@echo ""
	@echo "Test Artifacts:"
	@if [ -d "packages/lamina-core/test_artifacts" ]; then \
		echo "✅ Test artifacts directory exists"; \
		ls -la packages/lamina-core/test_artifacts/ | head -n 10; \
	else \
		echo "⚠️  No test artifacts directory"; \
	fi