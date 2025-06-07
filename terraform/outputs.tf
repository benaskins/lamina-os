output "repository_url" {
  description = "Repository URL"
  value       = github_repository.lamina_os.html_url
}

output "repository_ssh_url" {
  description = "Repository SSH URL"
  value       = github_repository.lamina_os.ssh_clone_url
}

output "repository_node_id" {
  description = "Repository Node ID for API calls"
  value       = github_repository.lamina_os.node_id
}