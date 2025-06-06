# Lamina OS Development Toolkit
# Test Management (ADR-0010) + Tool Management + GitOps Deployment

.PHONY: help test test-unit test-integration test-e2e test-all test-watch test-coverage clean-artifacts setup-test-env
.PHONY: tools tools-install tools-check tools-update tools-clean helm kubectl
.PHONY: gitops gitops-setup gitops-deploy gitops-status environment-check

# Tool Management Configuration
TOOLS_DIR := $(HOME)/.lamina/tools
HELM_VERSION := 3.14.0
KUBECTL_VERSION := 1.29.1
PLATFORM := $(shell uname -s | tr '[:upper:]' '[:lower:]')
ARCH := $(shell uname -m)

# Normalize architecture for download URLs
ifeq ($(ARCH),x86_64)
	DOWNLOAD_ARCH := amd64
else ifeq ($(ARCH),arm64)
	DOWNLOAD_ARCH := arm64
else ifeq ($(ARCH),aarch64)
	DOWNLOAD_ARCH := arm64
else
	DOWNLOAD_ARCH := $(ARCH)
endif

# Default target
help:
	@echo "🌊 Lamina OS Development Toolkit"
	@echo ""
	@echo "🔨 Build Commands (NEW - PREFERRED):"
	@echo "  check         Run all checks in containerized environment (CI simulation)"
	@echo "  format        Auto-format code with ruff in container"
	@echo "  lint          Run linting checks in container"
	@echo ""
	@echo "🧪 Test Commands:"
	@echo "  test          Run unit tests only (default, fast)"
	@echo "  test-unit     Run unit tests explicitly"  
	@echo "  test-integration  Run integration tests with Docker containers"
	@echo "  test-integration-local  Run integration tests locally (fallback)"
	@echo "  test-e2e      Run end-to-end tests (full system)"
	@echo "  test-all      Run all test tiers (unit + integration + e2e)"
	@echo "  test-watch    Run unit tests in watch mode"
	@echo "  test-coverage Generate test coverage report"
	@echo ""
	@echo "🔧 Tool Management:"
	@echo "  tools         Check all tool status"
	@echo "  tools-install Install all required tools (helm, kubectl)"
	@echo "  tools-check   Verify tool installations and versions"
	@echo "  tools-update  Update tools to latest versions"
	@echo "  tools-clean   Remove installed tools"
	@echo "  helm          Install/check Helm specifically"
	@echo "  kubectl       Install/check kubectl specifically"
	@echo ""
	@echo "🚀 GitOps Deployment:"
	@echo "  gitops-setup  Complete GitOps setup for production"
	@echo "  gitops-deploy Deploy to Kubernetes (requires tools)"
	@echo "  gitops-status Check deployment status"
	@echo "  environment-check  Validate environment configurations"
	@echo ""
	@echo "🌊 Unified CLI:"
	@echo "  cli-manifest  Show unified CLI plugin manifest"
	@echo "  cli-demo      Quick demo of unified CLI capabilities"
	@echo "  cli-test      Test unified CLI system"
	@echo ""
	@echo "🏗️ Infrastructure:"
	@echo "  setup-test-env    Set up test environment and LLM server"
	@echo "  clean-artifacts   Clean test artifacts and logs"
	@echo ""
	@echo "⚠️  Legacy Commands (deprecated, will be removed in v0.3.0):"
	@echo "  check-quality     Use 'make check' instead (containerized)"
	@echo "  dev-test          Use 'make test' instead"
	@echo "  ci-test           Use 'make test-all' instead"
	@echo ""
	@echo "Examples:"
	@echo "  make check                   # Run all checks (REQUIRED before commit)"
	@echo "  make format                  # Auto-fix formatting issues"
	@echo "  make test                    # Fast unit tests for development"
	@echo "  make test-integration        # Test with real AI models"
	@echo "  make tools-install           # Install helm + kubectl"
	@echo "  make gitops-setup            # Setup production GitOps"

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

# Development Workflow Shortcuts (DEPRECATED)
dev-test: test-unit
	@echo "⚠️  DEPRECATED: Use 'make test' directly instead of 'make dev-test'"
	@echo "This command will be removed in v0.3.0"
	@echo "💻 Development test cycle complete"

ci-test: test-all
	@echo "⚠️  DEPRECATED: Use 'make test-all' directly instead of 'make ci-test'"
	@echo "This command will be removed in v0.3.0"
	@echo "🚀 CI test cycle complete"

# Containerized Build System (NEW - PREFERRED)
check:
	@echo "🔍 Running containerized build checks (CI simulation)"
	@echo "Using build-env/ containerized environment..."
	@./scripts/check-build.sh

format:
	@echo "🎨 Auto-formatting code with containerized environment"
	@echo "Using build-env/ containerized environment..."
	@cd build-env && make format

lint:
	@echo "🔍 Running linting checks with containerized environment"
	@echo "Using build-env/ containerized environment..."
	@cd build-env && make lint

# Quality Gates (DEPRECATED)
check-quality:
	@echo "⚠️  DEPRECATED: Use 'make check' for containerized quality checks"
	@echo "This command uses direct uv commands instead of the containerized build environment"
	@echo "Recommended: 'make check' (ensures consistency with CI/CD)"
	@echo "This command will be removed in v0.3.0"
	@echo ""
	@echo "🔍 Running Quality Checks (Legacy Mode)"
	@echo ""
	@echo "Linting..."
	uv run ruff check packages/lamina-core/
	@echo ""
	@echo "Formatting..."
	uv run ruff format --check packages/lamina-core/
	@echo ""
	@echo "Type checking..."
	uv run mypy packages/lamina-core/ || echo "⚠️  Type checking issues found"
	@echo ""
	@echo "Security scanning..."
	uv run bandit -r packages/lamina-core/ || echo "⚠️  Security issues found"
	@echo ""
	@echo "✅ Quality checks completed (consider migrating to 'make check')"

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

# ==============================================================================
# Tool Management - Helm & kubectl for GitOps
# ==============================================================================

# Check all tools
tools: tools-check

tools-check:
	@echo "🔧 Checking Tool Status"
	@echo ""
	@echo "Platform: $(PLATFORM) $(DOWNLOAD_ARCH)"
	@echo "Tools Directory: $(TOOLS_DIR)"
	@echo ""
	@echo "Helm Status:"
	@if [ -f "$(TOOLS_DIR)/helm" ]; then \
		echo "✅ Helm installed: $$($(TOOLS_DIR)/helm version --short --client)"; \
	elif command -v helm >/dev/null 2>&1; then \
		echo "✅ Helm available (system): $$(helm version --short --client)"; \
	else \
		echo "❌ Helm not found"; \
	fi
	@echo ""
	@echo "kubectl Status:"
	@if [ -f "$(TOOLS_DIR)/kubectl" ]; then \
		echo "✅ kubectl installed: $$($(TOOLS_DIR)/kubectl version --client --output=yaml | grep gitVersion | head -n1 | sed 's/.*gitVersion: //')"; \
	elif command -v kubectl >/dev/null 2>&1; then \
		echo "✅ kubectl available (system): $$(kubectl version --client --output=yaml | grep gitVersion | head -n1 | sed 's/.*gitVersion: //')"; \
	else \
		echo "❌ kubectl not found"; \
	fi
	@echo ""
	@echo "To install missing tools: make tools-install"

# Install all tools
tools-install: helm kubectl
	@echo "🎉 All tools installed successfully!"
	@echo ""
	@echo "Tools available at: $(TOOLS_DIR)"
	@echo "Add to PATH: export PATH=\"$(TOOLS_DIR):\$$PATH\""
	@echo ""
	@echo "Or use project-managed tools with:"
	@echo "  make gitops-setup    # Uses project tools automatically"

# Install Helm
helm:
	@echo "🔧 Installing Helm $(HELM_VERSION)..."
	@mkdir -p $(TOOLS_DIR)
	@if [ -f "$(TOOLS_DIR)/helm" ]; then \
		INSTALLED_VERSION=$$($(TOOLS_DIR)/helm version --short --client | grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+'); \
		if [ "$$INSTALLED_VERSION" = "v$(HELM_VERSION)" ]; then \
			echo "✅ Helm $(HELM_VERSION) already installed"; \
			exit 0; \
		else \
			echo "🔄 Updating Helm from $$INSTALLED_VERSION to v$(HELM_VERSION)"; \
		fi \
	fi
	@echo "⬇️  Downloading Helm $(HELM_VERSION) for $(PLATFORM)-$(DOWNLOAD_ARCH)..."
	@cd $(TOOLS_DIR) && \
		curl -fsSL "https://get.helm.sh/helm-v$(HELM_VERSION)-$(PLATFORM)-$(DOWNLOAD_ARCH).tar.gz" | \
		tar -xzf - --strip-components=1 "$(PLATFORM)-$(DOWNLOAD_ARCH)/helm"
	@chmod +x $(TOOLS_DIR)/helm
	@echo "✅ Helm $(HELM_VERSION) installed successfully"
	@$(TOOLS_DIR)/helm version --short --client

# Install kubectl
kubectl:
	@echo "🔧 Installing kubectl $(KUBECTL_VERSION)..."
	@mkdir -p $(TOOLS_DIR)
	@if [ -f "$(TOOLS_DIR)/kubectl" ]; then \
		INSTALLED_VERSION=$$($(TOOLS_DIR)/kubectl version --client --output=yaml | grep gitVersion | head -n1 | sed 's/.*gitVersion: //' | tr -d '"'); \
		if [ "$$INSTALLED_VERSION" = "v$(KUBECTL_VERSION)" ]; then \
			echo "✅ kubectl $(KUBECTL_VERSION) already installed"; \
			exit 0; \
		else \
			echo "🔄 Updating kubectl from $$INSTALLED_VERSION to v$(KUBECTL_VERSION)"; \
		fi \
	fi
	@echo "⬇️  Downloading kubectl $(KUBECTL_VERSION) for $(PLATFORM)-$(DOWNLOAD_ARCH)..."
	@curl -fsSL "https://dl.k8s.io/release/v$(KUBECTL_VERSION)/bin/$(PLATFORM)/$(DOWNLOAD_ARCH)/kubectl" \
		-o $(TOOLS_DIR)/kubectl
	@chmod +x $(TOOLS_DIR)/kubectl
	@echo "✅ kubectl $(KUBECTL_VERSION) installed successfully"
	@$(TOOLS_DIR)/kubectl version --client --output=yaml | grep gitVersion | head -n1

# Update tools to latest versions (updates version variables and reinstalls)
tools-update:
	@echo "🔄 Updating tools to latest versions..."
	@echo "Current versions: Helm $(HELM_VERSION), kubectl $(KUBECTL_VERSION)"
	@echo ""
	@echo "⚠️  This will update to the versions specified in the Makefile"
	@echo "To get latest versions, update HELM_VERSION and KUBECTL_VERSION in Makefile"
	@echo ""
	@read -p "Continue with reinstall? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		rm -f $(TOOLS_DIR)/helm $(TOOLS_DIR)/kubectl; \
		$(MAKE) tools-install; \
	else \
		echo "Cancelled"; \
	fi

# Clean installed tools
tools-clean:
	@echo "🧹 Cleaning installed tools..."
	@if [ -d "$(TOOLS_DIR)" ]; then \
		echo "Removing: $(TOOLS_DIR)"; \
		rm -rf $(TOOLS_DIR); \
		echo "✅ Tools cleaned"; \
	else \
		echo "⚠️  No tools directory found"; \
	fi

# ==============================================================================
# GitOps Integration Commands
# ==============================================================================

# Environment check
environment-check:
	@echo "🌊 Validating Environment Configurations"
	@echo ""
	@cd packages/lamina-core && uv run lamina environment validate

# GitOps setup using project-managed tools
gitops-setup: tools-install
	@echo "🚀 Setting up GitOps for Production Environment"
	@echo ""
	@echo "Using project-managed tools:"
	@echo "  Helm: $(TOOLS_DIR)/helm"
	@echo "  kubectl: $(TOOLS_DIR)/kubectl"
	@echo ""
	@cd packages/lamina-core && PATH="$(TOOLS_DIR):$$PATH" uv run python -c "from lamina.cli.main import handle_gitops_command; \
		from argparse import Namespace; \
		args = Namespace(gitops_command='setup', environment='production', repo_url='https://github.com/benaskins/lamina-os', argocd=True); \
		handle_gitops_command(args)"

# GitOps deployment using project-managed tools  
gitops-deploy: tools-install
	@echo "🚀 Deploying to Production Kubernetes"
	@echo ""
	@cd packages/lamina-core && PATH="$(TOOLS_DIR):$$PATH" uv run python -c "from lamina.cli.main import handle_gitops_command; \
		from argparse import Namespace; \
		args = Namespace(gitops_command='deploy', environment='production', chart_path=None, namespace=None, dry_run=False, wait=True, timeout=600); \
		handle_gitops_command(args)"

# GitOps status using project-managed tools
gitops-status: tools-install
	@echo "📊 Checking Production Deployment Status"
	@echo ""
	@cd packages/lamina-core && PATH="$(TOOLS_DIR):$$PATH" uv run python -c "from lamina.cli.main import handle_gitops_command; \
		from argparse import Namespace; \
		args = Namespace(gitops_command='status', environment='production', namespace=None); \
		handle_gitops_command(args)"

# Helper for PATH setup instructions
show-path:
	@echo "🔧 Tool PATH Setup"
	@echo ""
	@echo "To use project-managed tools in your shell:"
	@echo "  export PATH=\"$(TOOLS_DIR):\$$PATH\""
	@echo ""
	@echo "Or add to your shell profile (~/.bashrc, ~/.zshrc):"
	@echo "  echo 'export PATH=\"$(TOOLS_DIR):\$$PATH\"' >> ~/.bashrc"
	@echo ""
	@echo "Current tools installed:"
	@if [ -d "$(TOOLS_DIR)" ]; then ls -la $(TOOLS_DIR)/; else echo "  No tools installed yet"; fi

# ==============================================================================
# Developer CLI Integration
# ==============================================================================

# Show unified CLI manifest
cli-manifest:
	@echo "🌊 Lamina Unified CLI Manifest"
	@echo ""
	@cd packages/lamina-core && uv run lamina --manifest

# Quick demo of unified CLI
cli-demo:
	@echo "🌊 Lamina Unified CLI Demo"
	@echo ""
	@echo "🏛️ Available environments:"
	@cd packages/lamina-core && uv run lamina environment list
	@echo ""
	@echo "📋 Available commands:"
	@cd packages/lamina-core && uv run lamina --help | grep -A 20 "Commands:"
	@echo ""
	@echo "💫 Try creating a sanctuary:"
	@echo "  cd /tmp && lamina sanctuary create my-test-sanctuary"

# Test the unified CLI system
cli-test:
	@echo "🧪 Testing Unified CLI System"
	@echo ""
	@echo "Testing environment operations..."
	@cd packages/lamina-core && uv run lamina environment list
	@echo ""
	@echo "Testing plugin manifest..."
	@cd packages/lamina-core && uv run lamina --manifest
	@echo ""
	@echo "✅ Unified CLI system operational"