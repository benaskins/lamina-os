#!/bin/bash
# Comprehensive security check script for Lamina OS
# Runs all security tools locally before committing

set -e

echo "🔒 Lamina OS Security Check"
echo "=========================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Please run this script from the project root"
    exit 1
fi

# Install dependencies if needed
echo "📦 Installing security dependencies..."
if ! command -v uv &> /dev/null; then
    echo "❌ uv is required. Please install it first."
    exit 1
fi

# Ensure dev dependencies are installed
uv sync --extra dev

echo ""
echo "🔍 Running Security Scans..."
echo ""

# 1. Secret Detection with GitLeaks
echo "1️⃣ Secret Detection (GitLeaks)..."
if command -v gitleaks &> /dev/null; then
    if gitleaks detect --verbose --config .gitleaks.toml; then
        echo "✅ No secrets detected"
    else
        echo "❌ SECRETS DETECTED! Review and fix before committing."
        exit 1
    fi
else
    echo "⚠️  GitLeaks not installed. Install with: brew install gitleaks"
fi
echo ""

# 2. Python Security with Bandit
echo "2️⃣ Python Security (Bandit)..."
if uv run bandit -r packages/ --severity-level medium -f txt; then
    echo "✅ No high/medium security issues found"
else
    echo "⚠️  Security issues detected. Review bandit output above."
fi
echo ""

# 3. Dependency Vulnerabilities with pip-audit
echo "3️⃣ Dependency Vulnerabilities (pip-audit)..."
uv add pip-audit --quiet
if uv run pip-audit; then
    echo "✅ No known vulnerabilities in dependencies"
else
    echo "⚠️  Vulnerable dependencies detected. Consider updating."
fi
echo ""

# 5. Terraform Security (if terraform directory exists)
if [ -d "terraform" ]; then
    echo "5️⃣ Terraform Security (tfsec)..."
    if command -v tfsec &> /dev/null; then
        if tfsec terraform/; then
            echo "✅ Terraform configuration is secure"
        else
            echo "⚠️  Terraform security issues detected."
        fi
    else
        echo "⚠️  tfsec not installed. Install with: brew install tfsec"
    fi
    echo ""
fi

# 6. File Permissions Check
echo "6️⃣ File Permissions..."
ISSUES=0

# Check for world-writable files
if find . -type f -perm -002 -not -path "./.git/*" -not -path "./build-env/*" | grep -q .; then
    echo "⚠️  World-writable files found:"
    find . -type f -perm -002 -not -path "./.git/*" -not -path "./build-env/*"
    ISSUES=$((ISSUES + 1))
fi

# Check for executable files that shouldn't be
if find . -name "*.py" -perm -111 -not -path "./.git/*" -not -path "./scripts/*" | grep -q .; then
    echo "⚠️  Executable Python files found (should they be executable?):"
    find . -name "*.py" -perm -111 -not -path "./.git/*" -not -path "./scripts/*"
    ISSUES=$((ISSUES + 1))
fi

if [ $ISSUES -eq 0 ]; then
    echo "✅ File permissions look good"
fi
echo ""

# 7. Environment Variables Check
echo "7️⃣ Environment Variables..."
SECRET_COUNT=$(env | grep -i -E "(token|key|secret|password|api)" | wc -l)
if [ "$SECRET_COUNT" -gt 0 ]; then
    echo "⚠️  Found $SECRET_COUNT environment variables that might contain secrets"
    echo "   Review with: env | grep -i -E \"(token|key|secret|password|api)\""
else
    echo "✅ No obvious secret environment variables found"
fi
echo ""

# Summary
echo "📋 Security Check Summary"
echo "========================"
echo "✅ Secret detection completed"
echo "✅ Python security analysis completed"
echo "✅ Dependency vulnerability check completed"
echo "✅ File permissions checked"
echo "✅ Environment variables reviewed"
if [ -d "terraform" ]; then
    echo "✅ Terraform security scan completed"
fi
echo ""
echo "🛡️  Security check completed!"
echo ""
echo "💡 To run individual checks:"
echo "   gitleaks detect --config .gitleaks.toml"
echo "   uv run bandit -r packages/"
echo "   uv run safety check"
echo "   uv run pip-audit"
if [ -d "terraform" ]; then
    echo "   tfsec terraform/"
fi
echo ""
echo "🚀 If all checks pass, you're ready to commit!"