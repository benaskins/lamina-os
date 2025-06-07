variable "github_token" {
  description = "GitHub personal access token"
  type        = string
  sensitive   = true
}

variable "repository_owner" {
  description = "GitHub repository owner/organization"
  type        = string
  default     = "benaskins"
}

variable "repository_name" {
  description = "GitHub repository name"
  type        = string
  default     = "lamina-os"
}