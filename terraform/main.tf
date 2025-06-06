# Repository configuration
resource "github_repository" "lamina_os" {
  name        = var.repository_name
  description = "Breath-based AI agent architecture"
  visibility  = "public"

  has_issues   = true
  has_projects = true
  has_wiki     = true

  allow_merge_commit     = true
  allow_squash_merge     = true
  allow_rebase_merge     = true
  delete_branch_on_merge = false

  # Repository features
  has_downloads = true
  
  # Security
  vulnerability_alerts = true
  
  # Template settings
  is_template = false
  
  # Archive on destroy
  archive_on_destroy = true

  # Topics/tags for the repository
  topics = [
    "ai",
    "agent-architecture", 
    "breath-first",
    "consciousness",
    "python",
    "lamina"
  ]
}

# Branch protection for main branch
resource "github_branch_protection" "main" {
  repository_id = github_repository.lamina_os.node_id
  pattern       = "main"

  required_status_checks {
    strict = true
    contexts = [
      "CI / test (3.11, unit)",
      "CI / test (3.12, unit)",
      "CI / test (3.13, unit)", 
      "CI / test (3.12, integration)",
      "CI / build"
    ]
  }

  enforce_admins = false

  required_pull_request_reviews {
    required_approving_review_count = 0
    dismiss_stale_reviews          = false
    require_code_owner_reviews     = false
    require_last_push_approval     = false
  }

  allows_deletions    = false
  allows_force_pushes = false
}

# Repository labels
resource "github_issue_label" "labels" {
  for_each = {
    bug = {
      color       = "d73a4a"
      description = "Something isn't working"
    }
    codex = {
      color       = "ededed"
      description = "AI assistant generated content"
    }
    documentation = {
      color       = "0075ca"
      description = "Improvements or additions to documentation"
    }
    duplicate = {
      color       = "cfd3d7"
      description = "This issue or pull request already exists"
    }
    enhancement = {
      color       = "a2eeef"
      description = "New feature or request"
    }
    "good first issue" = {
      color       = "7057ff"
      description = "Good for newcomers"
    }
    "help wanted" = {
      color       = "008672"
      description = "Extra attention is needed"
    }
    invalid = {
      color       = "e4e669"
      description = "This doesn't seem right"
    }
    lore = {
      color       = "c5def5"
      description = "System lore"
    }
    question = {
      color       = "d876e3"
      description = "Further information is requested"
    }
    speculative = {
      color       = "B95DD8"
      description = "Wild unproven ideas"
    }
    wontfix = {
      color       = "ffffff"
      description = "This will not be worked on"
    }
  }

  repository  = github_repository.lamina_os.name
  name        = each.key
  color       = each.value.color
  description = each.value.description
}