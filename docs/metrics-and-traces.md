# Metrics And Traces

OpenTelemetry provides a vendor-neutral way to collect telemetry from applications and infrastructure.

## Metrics

Useful application metrics include:

- request count
- request duration
- error rate
- queue depth
- worker processing time
- database latency

## Traces

Distributed traces help explain where time is spent across services. For ECS workloads, traces are useful when requests cross APIs, workers, queues, and databases.

## Collector Pattern

The collector can run as:

- a sidecar in the same ECS task
- a standalone ECS service
- an agent-style service per cluster

A standalone collector service is often easier to manage centrally, while a sidecar can be simpler for tightly coupled workloads.

## Practical Guidance

Start with logs and basic metrics. Add traces once service boundaries and instrumentation standards are clear.
