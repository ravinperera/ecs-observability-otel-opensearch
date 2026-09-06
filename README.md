# ECS Observability With OpenTelemetry And OpenSearch

ECS observability pattern using OpenTelemetry Collector, CloudWatch logs, FireLens, and OpenSearch.

This repository demonstrates a production-style observability approach for ECS Fargate workloads. It is intentionally generic and uses placeholder values only.

## 30-Second Quick Start

Use this repository as a reference pattern for understanding how ECS telemetry is produced, routed, and stored:

1. Start with the example ECS task definitions in [`ecs/`](ecs/) to see the application, FireLens, and OpenTelemetry components.
2. Review [`configs/fluent-bit-opensearch.conf`](configs/fluent-bit-opensearch.conf) for the container log-routing pattern.
3. Review [`configs/otel-collector-config.yaml`](configs/otel-collector-config.yaml) for the metrics and traces collection pattern.
4. Review the Terraform examples in [`terraform/`](terraform/) for supporting log groups and task IAM permissions.
5. Read the [logging strategy](docs/logging-strategy.md), [metrics and traces](docs/metrics-and-traces.md), [telemetry schema contract](docs/telemetry-contract.md), and [OpenSearch indexing](docs/opensearch-indexing.md) guides before adapting the pattern.

The basic telemetry flow is:

- Application containers write structured logs to `stdout` and `stderr`.
- FireLens or Fluent Bit routes those logs to CloudWatch Logs and, where appropriate, OpenSearch.
- Applications export metrics and traces to the OpenTelemetry Collector.
- The collector processes and forwards telemetry to the configured observability backends.

Files in `ecs/`, `configs/`, and `terraform/` are illustrative examples and configuration patterns. They contain placeholders and are not intended for direct production deployment without environment-specific security, networking, capacity, retention, and cost review.

## What This Demonstrates

- ECS service logging strategy using CloudWatch Logs
- FireLens log routing pattern for container logs
- OpenTelemetry Collector configuration for metrics and traces
- OpenSearch ingestion pattern for searchable operational logs
- Separation between application containers and observability sidecars/services
- Terraform examples for log groups, task definitions, and IAM permissions
- Practical notes on retention, indexes, security, alerting, and telemetry cost control

## Architecture

Application containers write structured logs to FireLens and export metrics and traces to the OpenTelemetry Collector. The routing layer then sends each signal to the appropriate CloudWatch or OpenSearch destination.

See the [telemetry architecture diagram](docs/architecture.md) for the separate log, metric, and trace flows, along with the main security and reliability boundaries.

## Repository Structure

```text
.
├── .github/workflows/
│   └── validate.yml
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
├── scripts/
│   └── validate_repository.py
├── docs/
│   ├── architecture.md
│   ├── cost-and-cardinality-guardrails.md
│   ├── logging-strategy.md
│   ├── metrics-and-traces.md
│   ├── opensearch-indexing.md
│   ├── production-rollout-checklist.md
│   ├── runbooks.md
│   ├── sensitive-telemetry-handling.md
│   ├── telemetry-contract.md
│   └── troubleshooting.md
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
- Treat telemetry volume and cardinality as production reliability concerns

## Guides

- [Telemetry architecture](docs/architecture.md)
- [Cost and cardinality guardrails](docs/cost-and-cardinality-guardrails.md)
- [Logging strategy](docs/logging-strategy.md)
- [Metrics and traces](docs/metrics-and-traces.md)
- [OpenSearch indexing](docs/opensearch-indexing.md)
- [Operational runbook examples](docs/runbooks.md)
- [Production rollout and rollback checklist](docs/production-rollout-checklist.md)
- [Sensitive telemetry handling](docs/sensitive-telemetry-handling.md)
- [Telemetry schema and attribute contract](docs/telemetry-contract.md)
- [Troubleshooting guide](docs/troubleshooting.md)

## Validation

The read-only GitHub Actions workflow runs on pull requests, pushes to `main`, and manual dispatches. It performs safe offline checks only:

- parses every JSON example with the Python standard library and rejects duplicate object keys;
- parses every YAML example with the pinned `PyYAML==6.0.2` dependency and rejects duplicate mapping keys;
- verifies that every configured OpenTelemetry telemetry pipeline keeps both the `memory_limiter` and `batch` processors, and that both processors are defined;
- verifies that Fluent Bit OpenSearch outputs keep `TLS On`, `AWS_Auth On`, and port `443`;
- verifies that Markdown files are UTF-8, have balanced fenced code blocks, and do not contain broken repository-local links;
- scans public documentation, ECS/configuration examples, and Terraform files for a narrow set of high-confidence credential shapes without printing matched values.

Run the same checks locally:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: PyYAML==6.0.2
.venv/bin/python scripts/validate_repository.py
```

The credential-shape scan is intentionally narrow. It catches obvious AWS access-key IDs, GitHub tokens, OpenAI-style API keys, and PEM private-key headers while allowing redacted placeholders. It is a regression guard for a public reference repository, not a replacement for organisation-wide secret scanning.

The workflow intentionally does **not** contact AWS, register ECS task definitions, connect to OpenSearch, start Fluent Bit, run an OpenTelemetry Collector binary, or verify Terraform against live providers. Those checks require environment-specific endpoints, credentials, plugins, network access, and production review. Passing this workflow confirms basic syntax and documentation structure only; it does not prove that the examples are deployment-ready.

The workflow uses `contents: read`, does not request secrets, and uses no `pull_request_target` trigger, so it is safe to run for public-fork pull requests.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidance, safety expectations, and the review checklist for observability examples.

## Example Use Case

This pattern fits ECS-hosted APIs, workers, and scheduled tasks where teams need searchable logs, deployment visibility, and a foundation for traces and metrics.

## Status

This is a public reference implementation for portfolio and architecture demonstration. It should be adapted and security-reviewed before production use.
