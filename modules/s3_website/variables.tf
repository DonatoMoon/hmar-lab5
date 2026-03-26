variable "bucket_name" {
  type = string
}

variable "index_document" {
  type    = string
  default = "index.html"
}

variable "api_url" {
  type        = string
  description = "The API Gateway URL to dynamically inject into the frontend"
}
