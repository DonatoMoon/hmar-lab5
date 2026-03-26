variable "api_name" {
  type        = string
  description = "Name of the API Gateway"
}

variable "lambda_invoke_arn" {
  type        = string
  description = "Execution ARN of the Lambda function for API Gateway integration"
}

variable "lambda_function_name" {
  type        = string
  description = "Name of the Lambda function for granting invoke permission"
}
