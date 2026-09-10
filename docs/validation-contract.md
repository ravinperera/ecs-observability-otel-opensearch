# Offline validation contract

This repository keeps its pull-request validation deliberately offline and credential-free. The checks are intended to catch regressions in the public reference material without contacting AWS, OpenSearch, ECS, or an OpenTelemetry Collector runtime.

## Canonical configuration files

Two files are part of the validation contract and must remain present at these paths:

- `configs/otel-collector-config.yaml` — the canonical OpenTelemetry Collector example used for pipeline reliability checks.
- `configs/fluent-bit-opensearch.conf` — the canonical Fluent Bit OpenSearch example used for encrypted and authenticated output checks.

The CI regression suite fails if either file is removed or renamed. This prevents a security or reliability check from silently disappearing simply because its input file is no longer present.

If a future restructuring intentionally moves one of these examples, update the required-file regression test and the validator path in the same pull request so the change remains explicit and reviewable.

## What validation proves

A successful validation run confirms that the tracked examples satisfy the repository's offline syntax, documentation, credential-hygiene, and configuration guardrails.

It does **not** prove that an AWS deployment is safe, that an OpenSearch endpoint is reachable, that IAM permissions are correct for a specific environment, or that the collector and Fluent Bit configurations are compatible with every runtime version. Those require environment-specific review and testing.
