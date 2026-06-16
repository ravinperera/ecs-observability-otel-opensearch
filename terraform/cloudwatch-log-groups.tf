terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

resource "aws_cloudwatch_log_group" "application" {
  name              = var.application_log_group_name
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "firelens" {
  name              = var.firelens_log_group_name
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "otel_collector" {
  name              = var.otel_log_group_name
  retention_in_days = var.log_retention_days
  tags              = var.tags
}
