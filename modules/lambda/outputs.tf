output "invoke_arn" {
  value       = aws_lambda_function.backend.invoke_arn
  description = "Invoke ARN of the Lambda function for API Gateway integration"
}

output "function_name" {
  value       = aws_lambda_function.backend.function_name
  description = "Name of the Lambda function"
}
