variable "prefix" {
  type        = string
  description = "Unique prefix for all resources (e.g., student name and variant)"
}

variable "alert_email" {
  type        = string
  description = "Email address for SNS alerts"
}
