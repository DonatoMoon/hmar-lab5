terraform {
  # Закоментовано для відкритого репозиторію.
  # Щоб використовувати AWS S3 як Backend, вкажіть назву свого власного унікального бакета.
  # backend "s3" {
  #   bucket       = "tf-state-lab4-your-name-variant"
  #   key          = "envs/dev/terraform.tfstate"
  #   region       = "eu-central-1"
  #   use_lockfile = true
  # }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.10.0"
}
