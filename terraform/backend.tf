# Terraform Cloud backend configuration
# Create workspace at https://app.terraform.io/
terraform {
  cloud {
    organization = "benaskins"  # Replace with your org name
    
    workspaces {
      name = "lamina-os-github"
    }
  }
}