terraform {
  backend "s3" {
    bucket       = "js-final-proj-tfstate-194169601943-dev"
    key          = "de-final-project/dev/terraform.tfstate"
    region       = "eu-west-2"
    encrypt      = true
    use_lockfile = true
  }
}