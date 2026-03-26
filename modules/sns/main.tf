resource "aws_sns_topic" "alerts" {
  name = var.topic_name

  tags = {
    Name      = var.topic_name
    Project   = "lab4-serverless"
    ManagedBy = "terraform"
  }
}

# Email-підписка: після terraform apply AWS надішле листа з підтвердженням
# ВАЖЛИВО: підписник ОБОВ'ЯЗКОВО повинен підтвердити підписку кліком у листі!
resource "aws_sns_topic_subscription" "email_alert" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}
