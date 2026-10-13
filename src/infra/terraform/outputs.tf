output "api_url" {
  description = "Public URL of the API."
  value       = aws_apigatewayv2_stage.default.invoke_url
}

output "artifacts_bucket" {
  description = "Bucket to upload model artifacts to (src/scripts/upload_model.py --bucket ...)."
  value       = aws_s3_bucket.artifacts.id
}

output "lambda_function_name" {
  description = "Lambda function name (for logs: aws logs tail /aws/lambda/<name> --follow)."
  value       = aws_lambda_function.api.function_name
}
