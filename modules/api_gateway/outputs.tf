output "api_endpoint" {
  value       = aws_apigatewayv2_api.http_api.api_endpoint
  description = "The default endpoint URL for the HTTP API"
}
