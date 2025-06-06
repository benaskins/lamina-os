#!/bin/bash
set -e

echo "🚀 Importing existing GitHub resources to Terraform..."

# Repository
echo "📦 Importing repository..."
terraform import github_repository.lamina_os lamina-os

# Branch protection
echo "🛡️ Importing branch protection..."
terraform import github_branch_protection.main benaskins/lamina-os:main

# Labels
echo "🏷️ Importing labels..."
terraform import 'github_issue_label.labels["bug"]' 'benaskins/lamina-os:bug'
terraform import 'github_issue_label.labels["codex"]' 'benaskins/lamina-os:codex'
terraform import 'github_issue_label.labels["documentation"]' 'benaskins/lamina-os:documentation'
terraform import 'github_issue_label.labels["duplicate"]' 'benaskins/lamina-os:duplicate'
terraform import 'github_issue_label.labels["enhancement"]' 'benaskins/lamina-os:enhancement'
terraform import 'github_issue_label.labels["good first issue"]' 'benaskins/lamina-os:good first issue'
terraform import 'github_issue_label.labels["help wanted"]' 'benaskins/lamina-os:help wanted'
terraform import 'github_issue_label.labels["invalid"]' 'benaskins/lamina-os:invalid'
terraform import 'github_issue_label.labels["lore"]' 'benaskins/lamina-os:lore'
terraform import 'github_issue_label.labels["question"]' 'benaskins/lamina-os:question'
terraform import 'github_issue_label.labels["speculative"]' 'benaskins/lamina-os:speculative'
terraform import 'github_issue_label.labels["wontfix"]' 'benaskins/lamina-os:wontfix'

echo "✅ Import complete! Run 'terraform plan' to verify."