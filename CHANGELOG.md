# Change History

This is a curated summary of **verified merged repository changes**, grouped by merge month. It is not a complete commit log, a set of published release versions, or evidence that any example was deployed or validated against live AWS, ECS, OpenTelemetry, Fluent Bit, or OpenSearch. See the linked pull requests for precise scope and test evidence.

## September 2026

- Added an explicit telemetry schema and attribute contract, plus a guide index and reading order ([PR #33](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/33), [PR #45](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/45)).
- Expanded offline regression-test discovery and required canonical Fluent Bit and OpenTelemetry configuration examples to remain present ([PR #42](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/42), [PR #43](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/43)).
- Added checks for required OpenTelemetry pipeline processors and secure Fluent Bit OpenSearch output settings ([PR #37](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/37), [PR #39](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/39)).
- Added a narrowly scoped, redaction-aware check for high-confidence credential-shaped values in public examples ([PR #35](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/35)).

## August 2026

- Made offline validation reject duplicate JSON object keys and YAML mapping keys, avoiding silent override of earlier values ([PR #29](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/29), [PR #31](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/31)).
- Added checks for repository-local Markdown links and image targets without requiring network access ([PR #27](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/27)).
- Added focused issue forms and guidance for reporting security-sensitive problems without exposing details in public issues ([PR #25](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/25), [PR #23](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/23)).
- Added regression tests for the offline example validator ([PR #21](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/21)).

## July 2026

- Introduced credential-free validation of JSON, YAML, and basic Markdown structure with read-only GitHub Actions ([PR #19](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/19)).
- Added a quick start and operational runbooks for common telemetry problems ([PR #17](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/17), [PR #18](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/18)).
- Added an architecture diagram and a staged production-rollout and rollback checklist ([PR #16](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/16), [PR #15](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/15)).
- Documented sensitive telemetry handling and cost/cardinality guardrails ([PR #13](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/13), [PR #11](https://github.com/ravinperera/ecs-observability-otel-opensearch/pull/11)).

Future additions should describe user-visible changes with supporting merged PRs and keep repository validation distinct from live environment or production acceptance.
