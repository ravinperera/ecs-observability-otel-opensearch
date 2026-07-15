# Production Rollout and Rollback Checklist

Introduce observability changes in stages. A telemetry pipeline must not reduce application availability, expose sensitive data, or create an unbounded operational cost.

## Before rollout

- [ ] Name the service owner, observability owner, and on-call contact.
- [ ] Document the signals being added and the decisions they support.
- [ ] Validate task definitions, collector configuration, IAM policies, and Terraform in a non-production environment.
- [ ] Confirm prohibited fields are removed and redaction tests pass.
- [ ] Set log retention, trace sampling, metric dimensions, index lifecycle, and budget alerts.
- [ ] Confirm collectors and routers have CPU and memory limits plus health checks.
- [ ] Define acceptable application latency, CPU, memory, error-rate, and task-restart thresholds.
- [ ] Record the previous task-definition revision and configuration versions.
- [ ] Prepare a tested disable or rollback path.

## Staged deployment

1. Deploy to development and generate representative traffic.
2. Confirm logs, metrics, and traces are complete, correctly attributed, and free of sensitive values.
3. Deploy to a low-risk production service or a small percentage of tasks.
4. Observe through at least one normal traffic peak before expanding.
5. Increase coverage gradually while comparing application and telemetry health to the baseline.

Avoid enabling verbose logging, full trace capture, or new high-cardinality dimensions at the same time as a major application release.

## Validation during rollout

Check both the application and the telemetry path:

- application latency, errors, CPU, memory, task health, and deployment stability
- FireLens or log-router restarts, retries, buffer use, and dropped records
- OpenTelemetry Collector queue size, export failures, refused telemetry, and memory limiter activity
- destination indexing latency, rejected writes, disk pressure, and search availability
- signal completeness, timestamps, environment labels, and service attribution
- unexpected fields, credentials, personal data, or request payloads
- ingestion volume, metric-series growth, trace volume, and projected cost

Record evidence and timestamps rather than relying only on a verbal confirmation.

## Stop or rollback conditions

Pause expansion and roll back when any agreed threshold is exceeded, including:

- measurable application latency or error-rate regression
- repeated task or sidecar restarts
- sustained collector queue growth or dropped telemetry
- destination write rejection or disk-watermark pressure
- sensitive-data exposure
- missing critical logs or traces needed for incident response
- telemetry volume or cardinality materially above the estimate
- loss of access control or environment separation

Security exposure requires immediate containment; do not wait for the normal observation window.

## Rollback procedure

1. Stop further deployment.
2. Restore the previous ECS task-definition revision or disable the affected exporter/router configuration.
3. Verify application health independently of the telemetry backend.
4. Drain or stop collectors safely where possible to avoid duplicate or corrupt delivery.
5. Restrict and remediate any affected telemetry destination.
6. Confirm task stability, error rate, latency, and resource use have returned to baseline.
7. Preserve configuration, metrics, and logs needed for root-cause analysis without copying sensitive values.
8. Open a follow-up issue with the failed assumption, evidence, owner, and retest criteria.

## After rollout

- [ ] Confirm dashboards and alerts have named owners and documented response actions.
- [ ] Verify retention and lifecycle policies are active, not merely configured in source.
- [ ] Review actual volume, cardinality, sampling, and cost after 24 hours and again after one normal business cycle.
- [ ] Test that loss of the telemetry destination does not take down the application.
- [ ] Update runbooks with known failure modes and rollback commands.
- [ ] Remove temporary debug settings and elevated access.
- [ ] Schedule a review after the first incident or material workload change.

A rollout is complete only when the team can detect pipeline failure, control its cost, protect its data, and reverse the change safely.
