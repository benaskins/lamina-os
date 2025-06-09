# Secrets Inventory

This document tracks where all sensitive credentials and secrets are stored across the Lamina OS development environment.

## 🔐 Local Machine Secrets

### Terraform Cloud Credentials
- **Location**: `~/.terraform.d/credentials.tfrc.json`
- **Contains**: Terraform Cloud API token for `app.terraform.io`
- **Used by**: Local `tofu` commands
- **Rotation**: Generate new token at https://app.terraform.io/app/settings/tokens

### GitHub CLI Authentication
- **Location**: Managed by `gh auth` (stored in keychain/credential manager)
- **Check status**: `gh auth status`
- **Rotation**: `gh auth refresh` or `gh auth login`
- **Scopes**: repo, admin:public_key, gist, read:org, workflow

### SSH Keys for Git
- **Location**: `~/.ssh/` (typically `id_rsa`, `id_ed25519`, etc.)
- **Check**: `ssh-add -l` and `ls ~/.ssh/*.pub`
- **Used by**: Git operations over SSH
- **Rotation**: Generate new keypair, update GitHub

### Environment Variables
- **Check for secrets**: `env | grep -i -E "(token|key|secret|password|api)"`
- **Common locations**: `~/.zshrc`, `~/.bashrc`, `~/.zprofile`

## ☁️ Cloud-Stored Secrets

### GitHub Repository Secrets
- **Location**: https://github.com/benaskins/lamina-os/settings/secrets/actions
- **Current secrets**:
  - `TF_API_TOKEN`: Terraform Cloud API token for CI/CD
  - `ANTHROPIC_API_KEY`: For Claude Code GitHub Actions (if configured)
- **Used by**: GitHub Actions workflows
- **Access**: Repository admins only

### Terraform Cloud Workspace Variables
- **Location**: https://app.terraform.io/app/lamina/lamina-os-github/variables
- **Current variables**:
  - `github_token` (sensitive): GitHub Personal Access Token
  - `repository_owner`: "benaskins" 
  - `repository_name`: "lamina-os"
- **Used by**: Terraform Cloud runs
- **Access**: Organization members with workspace permissions

## 🚫 Protected Locations (Never Commit)

### Local Files to Never Commit
```
~/.terraform.d/credentials.tfrc.json
terraform/terraform.tfvars
terraform/*.tfvars (except .example files)
.env*
.venv/pyvenv.cfg
sanctuary/local/
sanctuary/private/
*.pem, *.key, *.crt files
```

### Environment Files
```
.env.local
.env.development  
.env.production
.env
```

### Git Protections in Place
- **Main `.gitignore`**: Protects environment files, certificates, sanctuary configs
- **Terraform `.gitignore`**: Protects state files, variable files, credentials
- **Pre-commit hooks**: (if configured) scan for secrets before commit

## 🔄 Rotation Schedule

### Immediate Rotation Needed If:
- [ ] Token appears in logs, errors, or screenshots
- [ ] Token committed to git (even if reverted)
- [ ] Suspicious activity detected
- [ ] Team member access changes

### Regular Rotation (Recommended)
- **Terraform Cloud tokens**: Every 90 days
- **GitHub Personal Access Tokens**: Every 90 days  
- **SSH keys**: Annually or when compromised
- **API keys**: Per vendor recommendations

## 🚨 Emergency Procedures

### If Secrets Are Compromised:

1. **Immediate Actions**:
   ```bash
   # Revoke GitHub token
   gh auth refresh --scopes repo,workflow
   
   # Generate new Terraform Cloud token
   # Visit: https://app.terraform.io/app/settings/tokens
   
   # Update local credentials
   nano ~/.terraform.d/credentials.tfrc.json
   
   # Update GitHub secret
   # Visit: https://github.com/benaskins/lamina-os/settings/secrets/actions
   ```

2. **Verify No Unauthorized Changes**:
   ```bash
   # Check for repository changes
   gh api user/repos --paginate | jq '.[].full_name'
   
   # Check Terraform state
   cd terraform && tofu plan
   ```

3. **Update Documentation**:
   - Update this inventory
   - Document the incident
   - Review access logs

## 🔍 Audit Commands

### Check What's Currently Configured
```bash
# GitHub authentication
gh auth status

# Terraform credentials  
tofu version && tofu login --help

# SSH keys
ssh-add -l

# Environment variables (be careful with output)
env | grep -i -E "(token|key|secret)" | wc -l

# Git config (check for stored credentials)
git config --list | grep -E "(user|credential)"
```

### Scan for Accidentally Committed Secrets
```bash
# In repository root
git log --all --full-history -- "*.tfvars" "*.env*" "*secret*" "*key*"

# Search for patterns in history (use carefully)
git log -p --all | grep -E "(token|password|key)" | head -10
```

## 📋 Access Control

### Who Has Access to What:

**Local Machine**: Only Ben Askins
- Terraform credentials
- GitHub CLI auth
- SSH keys

**GitHub Repository Secrets**: Repository admins
- TF_API_TOKEN
- Any workflow secrets

**Terraform Cloud**: Organization members
- Workspace variables
- State files
- Plan/apply operations

## 🛡️ Best Practices

1. **Never hardcode secrets** in configuration files
2. **Use environment variables** or secret management for runtime secrets
3. **Rotate regularly** even if not compromised
4. **Audit access** periodically 
5. **Use least privilege** - only grant necessary scopes
6. **Monitor for leaks** in logs, errors, and version control

---

Last Updated: $(date)
Maintained by: Luthier
Review frequency: Monthly or after any security incident