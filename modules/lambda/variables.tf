variable "function_name" {
  type        = string
  description = "Name of the Lambda function"
}

variable "source_file" {
  type        = string
  description = "Path to the Python source code file"
}

variable "dynamodb_table_arn" {
  type        = string
  description = "ARN of the DynamoDB table for IAM policy"
}

variable "dynamodb_table_name" {
  type        = string
  description = "Name of the DynamoDB table for environment variable"
}

variable "sns_topic_arn" {
  type        = string
  description = "ARN of the SNS topic for IAM policy and environment variable"
}

variable "s3_bucket_arn" {
  type        = string
  description = "ARN of the S3 bucket for Polly audio"
}

variable "s3_bucket_name" {
  type        = string
  description = "Name of the S3 bucket for Polly audio"
}

variable "history_table_arn" {
  type        = string
  description = "ARN of the history DynamoDB table"
}

variable "history_table_name" {
  type        = string
  description = "Name of the history DynamoDB table"
}
