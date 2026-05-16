variable "aws_region" {
  description = "AWS region where resources will be created."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project prefix used to name AWS resources."
  type        = string
  default     = "lp-url-stats"
}

variable "stats_table_name" {
  description = "DynamoDB table name for daily URL statistics."
  type        = string
  default     = "url_stats"
}

variable "api_gateway_id" {
  description = "Existing HTTP API Gateway id where the stats route will be attached."
  type        = string
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}
