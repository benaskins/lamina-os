# Terraform Drift Detection Setup

This document explains how the automated drift detection works for the GitHub repository configuration.

## Overview

Drift detection automatically checks if manual changes were made to the GitHub repository outside of Terraform. This ensures all infrastructure changes go through code review.

## How It Works

### 1. Scheduled Checks (Every 6 Hours)
- Runs `tofu plan` to detect manual changes
- Creates a GitHub issue if drift is found
- Issue auto-closes when drift is resolved

### 2. Pull Request Checks
- Runs on any PR that touches `/terraform` directory
- Validates Terraform formatting and syntax
- Shows planned changes in PR comments
- Blocks merge if drift is detected

### 3. Manual Trigger
- Can be run anytime via Actions tab
- Useful for immediate drift verification

## Setup Requirements

### GitHub Secret Required

Add your Terraform Cloud API token as a GitHub secret:

1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Name: `TF_API_TOKEN`
4. Value: Your Terraform Cloud API token (from terraform.io)

### Labels Created Automatically

The workflow creates these labels if they don't exist:
- `drift-detection` - For drift detection issues
- `infrastructure` - For infrastructure-related PRs

## Responding to Drift

When drift is detected, you have two options:

### Option 1: Accept the Manual Changes
Update your Terraform config to match:
```bash
cd terraform/
tofu plan  # Review changes
# Edit main.tf to match current state
tofu plan  # Verify no changes
```

### Option 2: Revert to Desired State
```bash
cd terraform/
tofu apply  # Reverts manual changes
```

## Workflow Behaviors

### On Pull Requests
- Formats check (fails if `tofu fmt` needed)
- Validates configuration syntax
- Security scan with tfsec
- Shows plan in PR summary
- Comments on PR if drift detected

### On Schedule
- Runs every 6 hours
- Creates issue if drift found
- Only one issue at a time (won't spam)

### Manual Runs
- Available in Actions → Terraform Drift Detection
- Click "Run workflow" button

## Local Testing

Test the drift detection locally:
```bash
# Check for drift
cd terraform/
tofu plan -detailed-exitcode

# Exit codes:
# 0 = No changes (no drift)
# 2 = Changes detected (drift!)
# 1 = Error
```

## Troubleshooting

### Workflow Not Running
- Check if `TF_API_TOKEN` secret is set
- Verify Terraform Cloud organization and workspace names

### False Positives
Some fields may show drift due to API differences:
- Default values not shown in imports
- Computed fields that change

Update your Terraform config to match the actual values to resolve.

### Authentication Errors
- Regenerate Terraform Cloud API token
- Update `TF_API_TOKEN` secret in GitHub
- Check token has appropriate permissions