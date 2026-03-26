resource "aws_dynamodb_table" "main" {
  name         = var.table_name
  billing_mode = "PAY_PER_REQUEST"

  # Варіант #17: partition key = metric_name (String)
  hash_key = "metric_name"

  attribute {
    name = "metric_name"
    type = "S"
  }

  tags = {
    Name        = var.table_name
    Project     = "lab4-serverless"
    ManagedBy   = "terraform"
  }
}
