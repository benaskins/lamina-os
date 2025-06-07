# Terraform Cloud backend configuration
terraform {
  cloud {
    hostname     = "app.terraform.io"
    organization = "lamina"
    
    workspaces {
      name = "lamina-os-github"
    }
  }
}