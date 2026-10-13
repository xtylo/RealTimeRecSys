variable "aws_region" {
  description = "AWS region to deploy to."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name used for the Lambda function, IAM role, API and tags."
  type        = string
  default     = "realtime-recsys"
}

variable "artifacts_bucket_name" {
  description = "Globally unique S3 bucket name for model artifacts and the Lambda package (e.g. recsys-<your-name>-artifacts)."
  type        = string
}

variable "lambda_zip_path" {
  description = "Path to the package built by src/scripts/build_lambda.py, relative to this folder."
  type        = string
  default     = "../../../build/lambda.zip"
}

variable "enable_search" {
  description = "Enable the /search endpoint (LangChain + Bedrock embeddings)."
  type        = bool
  default     = false
}

variable "embeddings_model_id" {
  description = "Amazon Bedrock model used for embeddings."
  type        = string
  default     = "amazon.titan-embed-text-v2:0"
}

variable "lambda_memory_mb" {
  description = "Lambda memory. More memory also means more CPU (faster cold starts)."
  type        = number
  default     = 1024
}

variable "lambda_timeout_seconds" {
  description = "Lambda timeout in seconds."
  type        = number
  default     = 30
}

variable "log_retention_days" {
  description = "CloudWatch Logs retention."
  type        = number
  default     = 7
}
