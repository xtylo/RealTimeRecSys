# Infrastructure for RealTime RecSys:
#   API Gateway (HTTP API) -> Lambda (FastAPI + Mangum) -> S3 (model artifacts) / Bedrock (embeddings)

locals {
  artifacts_prefix = "models/v1"
  lambda_s3_key    = "lambda/${var.project_name}.zip"
}

# -----------------------------------------------------------------------------
# S3: model artifacts + Lambda deployment package
# -----------------------------------------------------------------------------
resource "aws_s3_bucket" "artifacts" {
  bucket        = var.artifacts_bucket_name
  force_destroy = true # portfolio project: let `terraform destroy` empty the bucket
}

resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket                  = aws_s3_bucket.artifacts.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# The package is ~50 MB zipped, right at the limit for direct uploads,
# so Lambda reads it from S3 instead (limit: 250 MB unzipped).
resource "aws_s3_object" "lambda_package" {
  bucket      = aws_s3_bucket.artifacts.id
  key         = local.lambda_s3_key
  source      = var.lambda_zip_path
  source_hash = filemd5(var.lambda_zip_path)
}

# -----------------------------------------------------------------------------
# IAM: least-privilege role for the Lambda function
# -----------------------------------------------------------------------------
data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "lambda" {
  name               = "${var.project_name}-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

data "aws_iam_policy_document" "lambda_permissions" {
  statement {
    sid       = "ReadModelArtifacts"
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.artifacts.arn}/${local.artifacts_prefix}/*"]
  }

  statement {
    sid       = "InvokeEmbeddingsModel"
    actions   = ["bedrock:InvokeModel"]
    resources = ["arn:aws:bedrock:${var.aws_region}::foundation-model/${var.embeddings_model_id}"]
  }
}

resource "aws_iam_role_policy" "lambda_permissions" {
  name   = "${var.project_name}-permissions"
  role   = aws_iam_role.lambda.id
  policy = data.aws_iam_policy_document.lambda_permissions.json
}

# -----------------------------------------------------------------------------
# Lambda: FastAPI app wrapped with Mangum (src/lambda/handler.py)
# -----------------------------------------------------------------------------
resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${var.project_name}"
  retention_in_days = var.log_retention_days
}

resource "aws_lambda_function" "api" {
  function_name    = var.project_name
  role             = aws_iam_role.lambda.arn
  runtime          = "python3.12"
  handler          = "handler.handler"
  architectures    = ["x86_64"]
  memory_size      = var.lambda_memory_mb
  timeout          = var.lambda_timeout_seconds
  s3_bucket        = aws_s3_object.lambda_package.bucket
  s3_key           = aws_s3_object.lambda_package.key
  source_code_hash = filebase64sha256(var.lambda_zip_path)

  environment {
    variables = {
      ARTIFACTS_SOURCE    = "s3"
      ARTIFACTS_BUCKET    = aws_s3_bucket.artifacts.id
      ARTIFACTS_PREFIX    = local.artifacts_prefix
      EMBEDDINGS_PROVIDER = "bedrock"
      ENABLE_SEARCH       = tostring(var.enable_search)
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda,
    aws_iam_role_policy_attachment.lambda_logs,
  ]
}

# -----------------------------------------------------------------------------
# API Gateway (HTTP API): every route goes to the Lambda; FastAPI does the routing
# -----------------------------------------------------------------------------
resource "aws_apigatewayv2_api" "http" {
  name          = var.project_name
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "default" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "api_gateway" {
  statement_id  = "AllowApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}
