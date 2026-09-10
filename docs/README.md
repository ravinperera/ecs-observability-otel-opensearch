# Observability guidance index

The documents in this directory turn the repository examples into a reviewable operating model rather than a collection of isolated configuration snippets. Use this index to choose the right level of detail for architecture review, implementation planning, security review, or incident preparation.

## Recommended reading order

1. [Telemetry architecture](architecture.md) — understand the ECS, OpenTelemetry, Fluent Bit, CloudWatch, and OpenSearch flow.
2. [Telemetry schema and attribute contract](telemetry-contract.md) — establish stable service/environment identity and schema-change expectations.
3. [Logging strategy](logging-strategy.md) and [Metrics and traces](metrics-and-traces.md) — understand the signal-specific design choices.
4. [Sensitive telemetry handling](sensitive-telemetry-handling.md) and [Cost and cardinality guardrails](cost-and-cardinality-guardrails.md) — review data-safety and spend/reliability boundaries.
5. [Production rollout and rollback checklist](production-rollout-checklist.md) — turn the reference pattern into a controlled environment-specific rollout.
6. [Operational runbooks](runbooks.md) and [Troubleshooting](troubleshooting.md) — prepare for degraded telemetry and service incidents.

## Architecture and data design

- [Telemetry architecture](architecture.md) — component boundaries and end-to-end signal flow.
- [Telemetry schema and attribute contract](telemetry-contract.md) — resource attributes, schema stability, compatibility, and evidence expectations.
- [Logging strategy](logging-strategy.md) — log routing and structure.
- [Metrics and traces](metrics-and-traces.md) — OpenTelemetry signal guidance.
- [OpenSearch indexing](opensearch-indexing.md) — indexing and lifecycle considerations.

## Security, reliability, and cost

- [Sensitive telemetry handling](sensitive-telemetry-handling.md) — reducing secrets, credentials, and sensitive payload exposure in telemetry.
- [Cost and cardinality guardrails](cost-and-cardinality-guardrails.md) — controlling high-cardinality labels and telemetry volume.
- [Offline validation contract](validation-contract.md) — what repository CI checks, which canonical configuration files are required, and what offline validation does not prove.

## Rollout and operations

- [Production rollout and rollback checklist](production-rollout-checklist.md) — environment-specific preflight, rollout, verification, and rollback planning.
- [Operational runbooks](runbooks.md) — response procedures for common observability failure modes.
- [Troubleshooting](troubleshooting.md) — investigation guidance for configuration and signal-delivery problems.

## Scope

These guides describe a public reference implementation. They are intended to make assumptions, controls, and operational decisions inspectable. They do not replace environment-specific IAM review, capacity testing, data-governance requirements, OpenSearch sizing, or production change approval.
