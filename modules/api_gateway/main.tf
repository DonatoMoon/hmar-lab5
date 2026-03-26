# ============================================================
# CloudWatch Log Group для API Gateway
# ============================================================
resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/aws/apigateway/${var.api_name}"
  retention_in_days = 7

  tags = {
    ManagedBy = "terraform"
  }
}

# ============================================================
# HTTP API (v2) — легший та дешевший за REST API
# ============================================================
resource "aws_apigatewayv2_api" "http_api" {
  name          = var.api_name
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET", "OPTIONS"]
    allow_headers = ["content-type"]
    max_age       = 300
  }

  tags = {
    Name      = var.api_name
    ManagedBy = "terraform"
  }
}

# Stage $default з автоматичним деплоєм
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http_api.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_logs.arn
    format          = "{ \"requestId\":\"$context.requestId\", \"ip\": \"$context.identity.sourceIp\", \"requestTime\":\"$context.requestTime\", \"httpMethod\":\"$context.httpMethod\",\"routeKey\":\"$context.routeKey\", \"status\":\"$context.status\",\"protocol\":\"$context.protocol\", \"responseLength\":\"$context.responseLength\" }"
  }
}

# Проксі-інтеграція з Lambda
# payload_format_version = "2.0" — сучасний формат event для HTTP API v2
resource "aws_apigatewayv2_integration" "lambda_integration" {
  api_id                 = aws_apigatewayv2_api.http_api.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = var.lambda_invoke_arn
  payload_format_version = "2.0"
}

# Маршрут: перенаправляє ВСІ методи та шляхи на Lambda
resource "aws_apigatewayv2_route" "any_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "metrics_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /metrics"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

resource "aws_apigatewayv2_route" "audio_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /alerts/{id}/audio"
  target    = "integrations/${aws_apigatewayv2_integration.lambda_integration.id}"
}

# Дозвіл для API Gateway викликати Lambda
# ВИПРАВЛЕНА ПОМИЛКА #2 З PDF:
# "/prod/GET" → "/*/*"
# Причина 1: stage називається $default, а не prod
# Причина 2: route "ANY /{proxy+}" — потрібні всі методи, не тільки GET
resource "aws_lambda_permission" "api_gw" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
