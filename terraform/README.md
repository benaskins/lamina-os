# GitHub Repository Terraform Configuration

This directory contains Terraform configuration to manage the `lamina-os` GitHub repository infrastructure as code, eliminating the need for manual "clickops" in the GitHub web interface.

## What This Manages

- ✅ **Repository settings** (description, visibility, features)
- ✅ **Branch protection rules** (required status checks, PR reviews)
- ✅ **Issue labels** (colors, descriptions)
- ✅ **Repository topics/tags**
- 🔄 **Future**: Webhooks, secrets, collaborators, teams

## Prerequisites

1. **Terraform Cloud account** - https://app.terraform.io/
2. **GitHub Personal Access Token** with scopes:
   - `repo` (full repository access)
   - `admin:repo_hook` (webhooks)
   - `delete_repo` (optional, for repo deletion)

## Setup Instructions

### 1. Create Terraform Cloud Workspace

1. Go to https://app.terraform.io/
2. Create organization: `benaskins` (or your preferred name)
3. Create workspace: `lamina-os-github`
4. Set workspace variables:
   - `github_token` (sensitive) - your GitHub PAT
   - `repository_owner` - "benaskins"
   - `repository_name` - "lamina-os"

### 2. Initialize Terraform

```bash
cd terraform/

# Authenticate with Terraform Cloud
terraform login

# Initialize backend and download providers
terraform init

# Verify configuration
terraform validate
```

### 3. Import Existing Resources

Since the repository already exists, import current state:

```bash
# Run the import script
./scripts/import-all.sh

# Or import manually (see import.tf for individual commands)
```

### 4. Plan and Apply

```bash
# See what changes Terraform will make
terraform plan

# Apply changes (should show no changes after import)
terraform apply
```

## Daily Workflow

### Making Repository Changes

1. **Edit Terraform files** instead of using GitHub web interface
2. **Plan changes** to see what will happen:
   ```bash
   terraform plan
   ```
3. **Apply changes**:
   ```bash
   terraform apply
   ```

### Adding New Labels

Edit `main.tf` and add to the `labels` map:

```hcl
resource "github_issue_label" "labels" {
  for_each = {
    # ... existing labels ...
    "new-label" = {
      color       = "ff0000"
      description = "New label description"
    }
  }
  # ...
}
```

### Updating Branch Protection

Modify the `github_branch_protection.main` resource in `main.tf`:

```hcl
resource "github_branch_protection" "main" {
  # ... existing config ...
  
  required_status_checks {
    strict = true
    contexts = [
      "CI / test (3.11, unit)",
      "CI / test (3.12, unit)",
      "CI / test (3.13, unit)",
      "CI / test (3.12, integration)", 
      "CI / build",
      "New Required Check"  # Add new required checks here
    ]
  }
}
```

## State Management

- **State stored in Terraform Cloud** (secure, versioned, collaborative)
- **No local state files** to manage
- **Automatic drift detection** - Terraform will detect manual changes
- **Change history** - full audit trail of infrastructure changes

## Security

- ✅ **GitHub token encrypted** in Terraform Cloud
- ✅ **State file secure** - never stored locally
- ✅ **No secrets in git** - `.gitignore` protects sensitive files
- ✅ **Access control** - Terraform Cloud manages permissions

## Troubleshooting

### Import Errors
If import fails, the resource might already be managed or have a different name:
```bash
# List resources in state
terraform state list

# Remove from state if needed
terraform state rm 'resource.name'

# Re-import with correct identifier
terraform import 'resource.name' 'github-identifier'
```

### Drift Detection
If someone makes manual changes in GitHub:
```bash
# Terraform will detect and show the drift
terraform plan

# Restore to desired state
terraform apply
```

### Authentication Issues
```bash
# Re-authenticate with Terraform Cloud
terraform login

# Verify GitHub token in workspace variables
# Check token scopes in GitHub settings
```

## File Structure

```
terraform/
├── backend.tf              # Terraform Cloud backend config
├── providers.tf            # GitHub provider configuration  
├── variables.tf            # Input variables
├── main.tf                 # Repository resources
├── outputs.tf              # Output values
├── import.tf               # Import commands reference
├── terraform.tfvars.example # Example variables file
├── scripts/
│   └── import-all.sh       # Automated import script
└── README.md              # This file
```

## Next Steps

After initial setup, consider adding:

- **Webhooks** for CI/CD integrations
- **Repository secrets** for Actions
- **Collaborator management** for team access
- **Multiple repositories** using modules
- **Environment-specific configurations**

---

🔨 **No more clickops!** All repository changes now go through code review and version control.