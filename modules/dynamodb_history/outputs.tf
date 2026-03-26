output "table_arn" {
  description = "ARN of the DynamoDB history table"
  value       = aws_dynamodb_table.main.arn
}

output "table_name" {
  description = "Name of the DynamoDB history table"
  value       = aws_dynamodb_table.main.name
}
