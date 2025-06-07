#!/bin/bash
# Secrets Audit Script for Lamina OS
# Provides a quick overview of where secrets are stored and their status

set -e

echo "🔐 Lamina OS Secrets Audit"
echo "=========================="
echo ""

# GitHub CLI Authentication
echo "📱 GitHub CLI Authentication:"
if gh auth status &>/dev/null; then
    gh auth status 2>&1 | head -5
    echo "✅ GitHub CLI authenticated"
else
    echo "❌ GitHub CLI not authenticated"
    echo "   Run: gh auth login"
fi
echo ""

# Terraform Cloud Credentials
echo "☁️  Terraform Cloud Credentials:"
if [ -f ~/.terraform.d/credentials.tfrc.json ]; then
    echo "✅ Terraform credentials file exists: ~/.terraform.d/credentials.tfrc.json"
    if jq empty ~/.terraform.d/credentials.tfrc.json 2>/dev/null; then
        HOSTNAME=$(jq -r '.credentials | keys[]' ~/.terraform.d/credentials.tfrc.json 2>/dev/null || echo "unknown")
        echo "   Configured for: $HOSTNAME"
    else
        echo "⚠️  Credentials file exists but invalid JSON"
    fi
else
    echo "❌ No Terraform credentials file found"
    echo "   Expected: ~/.terraform.d/credentials.tfrc.json"
fi
echo ""

# SSH Keys
echo "🔑 SSH Keys:"
if ssh-add -l &>/dev/null; then
    echo "✅ SSH agent running with keys:"
    ssh-add -l | sed 's/^/   /'
else
    echo "⚠️  No SSH keys in agent (or agent not running)"
fi

if ls ~/.ssh/*.pub &>/dev/null; then
    echo "📁 Public keys found:"
    ls ~/.ssh/*.pub | sed 's/^/   /'
else
    echo "❌ No SSH public keys found in ~/.ssh/"
fi
echo ""

# Git Configuration
echo "⚙️  Git Configuration:"
GIT_USER=$(git config --global user.name 2>/dev/null || echo "Not set")
GIT_EMAIL=$(git config --global user.email 2>/dev/null || echo "Not set")
echo "   User: $GIT_USER"
echo "   Email: $GIT_EMAIL"

CREDENTIAL_HELPER=$(git config --global credential.helper 2>/dev/null || echo "None")
echo "   Credential helper: $CREDENTIAL_HELPER"
echo ""

# Environment Variables Check
echo "🌍 Environment Variables:"
SECRET_COUNT=$(env | grep -i -E "(token|key|secret|password|api)" | wc -l)
if [ "$SECRET_COUNT" -gt 0 ]; then
    echo "⚠️  Found $SECRET_COUNT environment variables that might contain secrets"
    echo "   Review with: env | grep -i -E \"(token|key|secret|password|api)\""
else
    echo "✅ No obvious secret environment variables found"
fi
echo ""

# Terraform State Check
echo "🏗️  Terraform State:"
if [ -d "terraform" ]; then
    cd terraform
    if [ -f ".terraform/terraform.tfstate" ] || [ -f "terraform.tfstate" ]; then
        echo "⚠️  Local Terraform state found - may contain sensitive data"
        echo "   Consider using remote state backend"
    else
        echo "✅ No local state files found"
    fi
    
    if [ -f "terraform.tfvars" ]; then
        echo "⚠️  terraform.tfvars file found - ensure it's gitignored"
    else
        echo "✅ No terraform.tfvars file (good - use .example as template)"
    fi
    cd ..
else
    echo "ℹ️  No terraform directory found"
fi
echo ""

# GitHub Repository Secrets (if we can check)
echo "🐙 GitHub Repository Status:"
if gh auth status &>/dev/null; then
    REPO_NAME=$(gh repo view --json name -q .name 2>/dev/null || echo "unknown")
    echo "   Current repository: $REPO_NAME"
    echo "   Repository secrets: https://github.com/$(gh repo view --json owner,name -q '.owner.login + "/" + .name')/settings/secrets/actions"
else
    echo "❌ Cannot check repository status - GitHub CLI not authenticated"
fi
echo ""

# Security Recommendations
echo "🛡️  Security Recommendations:"
echo "   1. Rotate tokens every 90 days"
echo "   2. Use repository secrets for CI/CD"
echo "   3. Never commit .tfvars or .env files"
echo "   4. Review access permissions regularly"
echo "   5. Monitor for leaked credentials"
echo ""

# File Permissions Check
echo "🔒 File Permissions:"
if [ -f ~/.terraform.d/credentials.tfrc.json ]; then
    CRED_PERMS=$(stat -f "%A" ~/.terraform.d/credentials.tfrc.json 2>/dev/null || stat -c "%a" ~/.terraform.d/credentials.tfrc.json 2>/dev/null || echo "unknown")
    if [ "$CRED_PERMS" = "600" ]; then
        echo "✅ Terraform credentials properly secured (600)"
    else
        echo "⚠️  Terraform credentials permissions: $CRED_PERMS (should be 600)"
        echo "   Fix with: chmod 600 ~/.terraform.d/credentials.tfrc.json"
    fi
fi

if ls ~/.ssh/id_* &>/dev/null; then
    for key in ~/.ssh/id_*; do
        if [[ ! "$key" == *.pub ]]; then
            KEY_PERMS=$(stat -f "%A" "$key" 2>/dev/null || stat -c "%a" "$key" 2>/dev/null || echo "unknown")
            if [ "$KEY_PERMS" = "600" ]; then
                echo "✅ SSH key $(basename $key) properly secured (600)"
            else
                echo "⚠️  SSH key $(basename $key) permissions: $KEY_PERMS (should be 600)"
                echo "   Fix with: chmod 600 $key"
            fi
        fi
    done
fi

echo ""
echo "Audit completed at $(date)"
echo "For detailed secrets inventory, see: docs/SECRETS_INVENTORY.md"