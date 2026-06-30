# ECS Observability With OpenTelemetry And OpenSearch

ECS observability pattern using OpenTelemetry Collector, CloudWatch logs, FireLens, and OpenSearch.

This repository demonstrates a production-style observability approach for ECS Fargate workloads. It is intentionally generic and uses placeholder values only.

## What This Demonstrates

- ECS service logging strategy using CloudWatch Logs
- FireLens log routing pattern for container logs
- OpenTelemetry Collector configuration for metrics and traces
- OpenSearch ingestion pattern for searchable operational logs
- Separation between application containers and observability sidecars/services
- Terraform examples for log groups, task definitions, and IAM permissions
- Practical notes on retention, indexes, security, and alerting

## Architecture

```text
Application container
   |
   | stdout/stderr
   v
FireLens / Fluent Bit
   |
   +--> CloudWatch Logs
   +--> OpenSearch

Application metrics/traces
   |
   v
OpenTelemetry Collector
   |
   +--> CloudWatch metrics/logs
   +--> OpenSearch-compatible observability backend
```

## Repository Structure

```text
.
├── configs/
│   ├── otel-collector-config.yaml
│   └── fluent-bit-opensearch.conf
├── ecs/
│   ├── application-task-definition.json
│   └── otel-collector-task-definition.json
├── terraform/
│   ├── cloudwatch-log-groups.tf
│   ├── ecs-task-iam.tf
│   └── variables.tf
├── docs/
│   ├── logging-strategy.md
│   ├── metrics-and-traces.md
│   └── opensearch-indexing.md
├── CONTRIBUTING.md
└── README.md
```

## Design Principles

- Keep application logging simple: write structured logs to stdout/stderr
- Route logs centrally using FireLens or a collector layer
- Use OpenTelemetry for metrics and traces where possible
- Apply retention policies to CloudWatch log groups
- Avoid sending secrets or sensitive payloads into logs
- Use per-environment OpenSearch indexes
- Keep observability IAM permissions narrow and auditable

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance, safety expectations, and the review checklist for observability examples.

## Example Use Case

This pattern fits ECS-hosted APIs, workers, and scheduled tasks where teams need searchable logs, deployment visibility, and a foundation for traces and metrics.

## Status

This is a public reference implementation for portfolio and architecture demonstration. It should be adapted and security-reviewed before production use.
