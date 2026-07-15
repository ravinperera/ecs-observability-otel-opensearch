# Telemetry Cost and Cardinality Guardrails

Observability should reduce operational risk without creating an uncontrolled data bill. Apply these guardrails before enabling production ingestion.

## Start with explicit budgets

Define a monthly budget and expected daily volume for each environment. Track at least:

- CloudWatch log ingestion and retained storage
- OpenSearch data-node, storage, and snapshot cost
- Trace ingestion and retained spans
- Custom metric count and API usage
- Cross-AZ or internet data transfer caused by exporters

Alert on both absolute spend and sudden percentage changes. A 30–50% day-over-day increase is often more useful than a static threshold during early adoption.

## Logs

- Prefer structured application logs with a stable schema.
- Default production log level to `INFO`; enable `DEBUG` only for a time-bounded investigation.
- Exclude health-check noise and repeated successful polling where it has little diagnostic value.
- Do not log request or response bodies by default.
- Set environment-specific retention. Development logs commonly need days, not months.
- Use OpenSearch index lifecycle policies to roll over and delete old indexes.

Review the top log-producing services weekly during rollout. Unexpected volume usually comes from loops, stack traces, access logs, or verbose third-party libraries.

## Metrics and cardinality

Metric cost and performance are driven by the number of unique time series. Avoid labels whose values grow without a fixed bound, including:

- request, trace, session, or user identifiers
- raw URLs containing IDs
- timestamps
- exception messages
- container or task identifiers when service-level metrics are sufficient

Prefer bounded dimensions such as `service`, `environment`, `region`, `operation`, and a small controlled set of status classes.

Before adding a label, estimate:

```text
series = metric names × unique value combinations × environments
```

Reject dimensions that can create thousands of series without a clear operational decision they support.

## Traces

- Use head sampling as a simple baseline and increase sampling only for high-value services.
- Prefer tail sampling when error, latency, or route-aware decisions justify the added collector capacity.
- Always retain errors and unusually slow traces where the backend supports policy-based sampling.
- Avoid attaching sensitive payloads or unbounded attributes to spans.
- Document the sampling rate so dashboards and service-level indicators are interpreted correctly.

A reasonable starting point for healthy high-volume traffic is often 1–10%, with higher rates for low-volume or critical paths. Validate the result against actual incident-investigation needs.

## OpenSearch capacity

- Use separate indexes or data streams per environment and workload class.
- Configure rollover by size and age rather than allowing indefinitely growing indexes.
- Keep shard counts proportional to data volume; many small shards waste memory and CPU.
- Monitor disk watermarks, indexing latency, rejected writes, JVM pressure, and search latency.
- Test restore procedures before relying on snapshots as a recovery control.

## Deployment review checklist

Before enabling a new signal, confirm:

- [ ] An owner and operational use case are documented.
- [ ] Expected events, spans, or series per day are estimated.
- [ ] Retention and deletion settings are explicit.
- [ ] High-cardinality and sensitive fields are removed or transformed.
- [ ] Sampling and log-level defaults are recorded.
- [ ] Budget alerts and volume dashboards exist.
- [ ] A rollback or disable switch is available.

## Review signals

Investigate when any of these occur:

- telemetry volume grows faster than application traffic
- cardinality rises sharply after a release
- OpenSearch shard count grows without matching data growth
- collector queues, retries, or dropped-data counters increase
- debug logging remains enabled beyond the approved window
- observability cost materially exceeds its agreed budget

Treat these as engineering defects, not only finance concerns: uncontrolled telemetry can reduce platform reliability and obscure the signals operators actually need.
