variable "name" {
  description = "Name prefix for observability resources."
  type        = string
  default     = "sample-api"
}

variable "application_log_group_name" {
  description = "CloudWatch log group for application logs."
  type        = string
  default     = "/ecs/sample-api"
}

variable "firelens_log_group_name" {
  description = "CloudWatch log group for FireLens logs."
  type        = string
  default     = "/ecs/firelens"
}

variable "otel_log_group_name" {
  description = "CloudWatch log group for OpenTelemetry Collector logs."
  type        = string
  default     = "/ecs/otel-collector"
}

variable "log_retention_days" {
  description = "Log retention period in days."
  type        = number
  default     = 30
}

variable "opensearch_domain_arn" {
  description = "OpenSearch domain ARN."
  type        = string
  default     = "arn:aws:es:eu-west-2:111122223333:domain/example-observability"
}

variable "tags" {
  description = "Tags applied to supported resources."
  type        = map(string)
  default     = {}
}
