#!/bin/bash
# Fast build check script with intelligent fallbacks

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Running fast build checks...${NC}"

# Function to check if we can run natively
can_run_native() {
    command -v uv >/dev/null 2>&1 && \
    [ -f "pyproject.toml" ] && \
    [ -d ".venv" ] || uv sync --quiet >/dev/null 2>&1
}

# Function to run native checks
run_native_checks() {
    echo -e "${GREEN}⚡ Running native checks (fastest)...${NC}"
    
    echo -e "${YELLOW}=== Ruff Lint ===${NC}"
    uv run ruff check
    
    echo -e "${YELLOW}=== Ruff Format Check ===${NC}"
    uv run ruff format --check
    
    echo -e "${YELLOW}=== Core Tests ===${NC}"
    uv run pytest packages/lamina-core/tests/ -x --tb=short
    
    echo -e "${GREEN}✅ All native checks passed!${NC}"
}

# Function to run containerized checks
run_containerized_checks() {
    echo -e "${YELLOW}🐳 Running containerized checks...${NC}"
    
    # Change to build-env directory
    cd "$(dirname "$0")/../build-env"
    
    # Check if fast container exists
    if docker images -q lamina-build:fast > /dev/null 2>&1; then
        echo -e "${GREEN}📦 Using cached container...${NC}"
        make -f Makefile.fast check-fast
    else
        echo -e "${BLUE}🔨 Building optimized container...${NC}"
        make -f Makefile.fast check
    fi
}

# Function to run hybrid approach
run_hybrid_checks() {
    echo -e "${BLUE}🔄 Running hybrid checks (native linting + containerized tests)...${NC}"
    
    # Fast native linting
    echo -e "${YELLOW}=== Native Ruff Checks ===${NC}"
    uv run ruff check --fix
    uv run ruff format
    
    # Containerized tests for environment consistency
    echo -e "${YELLOW}=== Containerized Tests ===${NC}"
    cd "$(dirname "$0")/../build-env"
    if docker images -q lamina-build:fast > /dev/null 2>&1; then
        make -f Makefile.fast test
    else
        echo -e "${RED}⚠️  Fast container not available, building...${NC}"
        make -f Makefile.fast test
    fi
}

# Main logic
main() {
    # Check command line arguments
    case "${1:-auto}" in
        "native"|"local")
            if can_run_native; then
                run_native_checks
            else
                echo -e "${RED}❌ Native environment not ready. Falling back to containerized.${NC}"
                run_containerized_checks
            fi
            ;;
        "docker"|"container")
            run_containerized_checks
            ;;
        "hybrid")
            if can_run_native; then
                run_hybrid_checks
            else
                echo -e "${RED}❌ Native environment not ready. Using full containerized.${NC}"
                run_containerized_checks
            fi
            ;;
        "auto"|*)
            # Auto-detect best approach
            if can_run_native && docker --version >/dev/null 2>&1; then
                echo -e "${BLUE}🧠 Auto-detected: Using hybrid approach${NC}"
                run_hybrid_checks
            elif can_run_native; then
                echo -e "${BLUE}🧠 Auto-detected: Using native approach${NC}"
                run_native_checks
            else
                echo -e "${BLUE}🧠 Auto-detected: Using containerized approach${NC}"
                run_containerized_checks
            fi
            ;;
    esac
}

# Help text
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "Fast build check script"
    echo "Usage: $0 [mode]"
    echo ""
    echo "Modes:"
    echo "  auto     - Auto-detect best approach (default)"
    echo "  native   - Run checks natively with uv"
    echo "  docker   - Run checks in container"
    echo "  hybrid   - Native linting + containerized tests"
    echo ""
    echo "Examples:"
    echo "  $0                    # Auto-detect"
    echo "  $0 native            # Force native"
    echo "  $0 hybrid            # Hybrid approach"
    exit 0
fi

# Run main logic
main "$@"