variable "aws_region" {
  description = "AWS region where resources will be created."
  type        = string
}

variable "project_name" {
  description = "Project prefix used to name AWS resources."
  type        = string
}

variable "stats_table_name" {
  description = "DynamoDB table name for daily URL statistics."
  type        = string
}

variable "url_table_name" {
  description = "DynamoDB table name for URL records."
  type        = string
}

variable "api_gateway_id" {
  description = "Existing HTTP API Gateway id where the stats route will be attached."
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]{10}$", var.api_gateway_id))
    error_message = "api_gateway_id must be the 10-character API id from the execute-api URL."
  }
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
}
