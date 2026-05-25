data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../src"
  output_path = "${path.module}/lambda.zip"

  excludes = [
    "__pycache__",
    "**/__pycache__",
    "*.pyc",
    "**/*.pyc",
  ]
}

data "aws_caller_identity" "current" {}

data "aws_partition" "current" {}
