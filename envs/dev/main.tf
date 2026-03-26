provider "aws" {
  region = "eu-central-1"
}

# ============================================================
# locals — єдине місце для префіксу іменування ресурсів
# Змінити один раз тут → всі ресурси отримають правильні імена
# ============================================================
locals {
  prefix      = var.prefix
  alert_email = var.alert_email
}

# ============================================================
# Модуль 1: DynamoDB — таблиця з порогами
# Структура запису: { metric_name: "cpu_usage", threshold: 80 }
# ============================================================
module "database" {
  source     = "../../modules/dynamodb"
  table_name = "${local.prefix}-table"
}

# ============================================================
# Модуль 1.5: DynamoDB — таблиця з історією метрик та алертами
# Структура запису: { metric_name: "cpu_usage", timestamp: "2024-...", value: 85, is_alert: true }
# ============================================================
module "history_database" {
  source     = "../../modules/dynamodb_history"
  table_name = "${local.prefix}-history-table"
}

# ============================================================
# Модуль 2: SNS — топік для email-алертів
# ============================================================
module "alerts" {
  source      = "../../modules/sns"
  topic_name  = "${local.prefix}-alerts"
  alert_email = local.alert_email
}

# ============================================================
# Модуль 3: Lambda — бізнес-логіка threshold alerts
# ============================================================
module "backend" {
  source = "../../modules/lambda"

  function_name       = "${local.prefix}-lambda"
  source_file         = "${path.root}/../../src/app.py"
  dynamodb_table_arn  = module.database.table_arn
  dynamodb_table_name = module.database.table_name
  sns_topic_arn       = module.alerts.topic_arn
  s3_bucket_arn       = module.storage.bucket_arn
  s3_bucket_name      = module.storage.bucket_name
  history_table_arn   = module.history_database.table_arn
  history_table_name  = module.history_database.table_name
}

# ============================================================
# Модуль S3 — бакет для збереження аудіо
# ============================================================
module "storage" {
  source      = "../../modules/s3"
  bucket_name = "${local.prefix}-audio-bucket"
}

# ============================================================
# Модуль S3 Website — статичний хостинг для дашборду
# ============================================================
module "frontend" {
  source      = "../../modules/s3_website"
  bucket_name = "${local.prefix}-dashboard-bucket"
  api_url     = module.api.api_endpoint
}

# ============================================================
# Модуль 4: API Gateway HTTP API v2
# ============================================================
module "api" {
  source = "../../modules/api_gateway"

  api_name             = "${local.prefix}-api"
  lambda_invoke_arn    = module.backend.invoke_arn
  lambda_function_name = module.backend.function_name
}

# ============================================================
# Outputs
# ============================================================
output "api_url" {
  description = "Base URL для тестування: POST {api_url}/metrics, GET {api_url}/metrics"
  value       = module.api.api_endpoint
}

output "dashboard_url" {
  description = "URL вашого дашборду"
  value       = "http://${module.frontend.website_endpoint}"
}

output "dynamodb_table_name" {
  description = "Ім'я DynamoDB таблиці (для seed data)"
  value       = module.database.table_name
}

output "sns_topic_arn" {
  description = "ARN SNS топіку (для перевірки підписки)"
  value       = module.alerts.topic_arn
}

output "lambda_function_name" {
  description = "Ім'я Lambda (для перегляду логів у CloudWatch)"
  value       = module.backend.function_name
}
