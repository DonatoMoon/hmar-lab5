variable "topic_name" {
  type        = string
  description = "Name of the SNS topic"
}

variable "alert_email" {
  type        = string
  description = "Email address for SNS topic subscription"
}
