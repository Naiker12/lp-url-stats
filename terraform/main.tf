locals {
  resource_prefix   = "${var.project_name}-${var.environment}"
  api_execution_arn = "arn:${data.aws_partition.current.partition}:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${var.api_gateway_id}"
  stats_table_arn   = "arn:${data.aws_partition.current.partition}:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.stats_table_name}"
  urls_table_arn    = "arn:${data.aws_partition.current.partition}:dynamodb:${var.aws_region}:${data.aws_caller_identity.current.account_id}:table/${var.url_table_name}"
}

resource "aws_iam_role" "lambda_role" {
  name = "${local.resource_prefix}-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_policy" {
  name = "${local.resource_prefix}-lambda-policy"
  role = aws_iam_role.lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect   = "Allow"
        Action   = "dynamodb:Query"
        Resource = local.stats_table_arn
      },
      {
        Effect   = "Allow"
        Action   = "dynamodb:Scan"
        Resource = local.stats_table_arn
      },
      {
        Effect   = "Allow"
        Action   = "dynamodb:GetItem"
        Resource = local.urls_table_arn
      }
    ]
  })
}

resource "aws_lambda_function" "stats" {
  function_name    = "${local.resource_prefix}-stats"
  role             = aws_iam_role.lambda_role.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  memory_size      = 256
  timeout          = 10

  environment {
    variables = {
      STATS_TABLE_NAME = var.stats_table_name
      URL_TABLE_NAME   = var.url_table_name
    }
  }
}

resource "aws_apigatewayv2_integration" "stats" {
  api_id                 = var.api_gateway_id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.stats.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "stats" {
  api_id    = var.api_gateway_id
  route_key = "GET /stats/{codigo}"
  target    = "integrations/${aws_apigatewayv2_integration.stats.id}"
}

resource "aws_apigatewayv2_route" "stats_all" {
  api_id    = var.api_gateway_id
  route_key = "GET /stats"
  target    = "integrations/${aws_apigatewayv2_integration.stats.id}"
}

resource "aws_lambda_permission" "allow_api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.stats.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${local.api_execution_arn}/*/*"
}

output "lambda_function_name" {
  description = "Lambda function name."
  value       = aws_lambda_function.stats.function_name
}
