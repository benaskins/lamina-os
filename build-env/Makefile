# Build Environment Makefile
.PHONY: all check format lint test build shell clean

# Build the container
build:
	DOCKER_BUILDKIT=0 docker build -t lamina-build:latest -f Dockerfile ..

# Run all checks (mimics CI)
check: build
	docker run --rm -v $(PWD)/..:/workspace lamina-build:latest bash -c "\
		echo '=== Running Ruff Lint ===' && \
		uv run ruff check && \
		echo '=== Running Ruff Format Check ===' && \
		uv run ruff format --check && \
		echo '=== Running Bandit Security Check ===' && \
		uv run bandit -r packages/ || true && \
		echo '=== Running Tests ===' && \
		uv run pytest packages/lamina-core/tests/ -v"

# Auto-format code
format: build
	docker run --rm -v $(PWD)/..:/workspace lamina-build:latest bash -c "\
		uv run ruff check --fix && \
		uv run ruff format"

# Just run linting
lint: build
	docker run --rm -v $(PWD)/..:/workspace lamina-build:latest bash -c "\
		uv run ruff check && \
		uv run ruff format --check"

# Just run tests
test: build
	docker run --rm -v $(PWD)/..:/workspace lamina-build:latest \
		uv run pytest packages/lamina-core/tests/ -v

# Interactive shell for debugging
shell: build
	docker run --rm -it -v $(PWD)/..:/workspace lamina-build:latest bash

# Clean up
clean:
	docker rmi lamina-build:latest || true