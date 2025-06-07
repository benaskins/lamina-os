#!/bin/bash
set -e

echo "🚀 Importing existing GitHub resources to OpenTofu..."

# Repository
echo "📦 Importing repository..."
tofu import github_repository.lamina_os lamina-os

# Branch protection
echo "🛡️ Importing branch protection..."
tofu import github_branch_protection.main benaskins/lamina-os:main

# Labels
echo "🏷️ Importing labels..."
tofu import 'github_issue_label.labels["bug"]' 'benaskins/lamina-os:bug'
tofu import 'github_issue_label.labels["codex"]' 'benaskins/lamina-os:codex'
tofu import 'github_issue_label.labels["documentation"]' 'benaskins/lamina-os:documentation'
tofu import 'github_issue_label.labels["duplicate"]' 'benaskins/lamina-os:duplicate'
tofu import 'github_issue_label.labels["enhancement"]' 'benaskins/lamina-os:enhancement'
tofu import 'github_issue_label.labels["good first issue"]' 'benaskins/lamina-os:good first issue'
tofu import 'github_issue_label.labels["help wanted"]' 'benaskins/lamina-os:help wanted'
tofu import 'github_issue_label.labels["invalid"]' 'benaskins/lamina-os:invalid'
tofu import 'github_issue_label.labels["lore"]' 'benaskins/lamina-os:lore'
tofu import 'github_issue_label.labels["question"]' 'benaskins/lamina-os:question'
tofu import 'github_issue_label.labels["speculative"]' 'benaskins/lamina-os:speculative'
tofu import 'github_issue_label.labels["wontfix"]' 'benaskins/lamina-os:wontfix'

echo "✅ Import complete! Run 'tofu plan' to verify."