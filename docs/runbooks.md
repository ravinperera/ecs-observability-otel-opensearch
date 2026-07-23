# Operational Runbook Examples

These example runbooks show how an on-call engineer can respond when an ECS observability signal indicates a service or telemetry-path problem.

They are intentionally generic. Replace placeholders with environment-specific dashboards, alarms, owners, escalation paths, retention rules, and change procedures before production use.

Use the [troubleshooting guide](troubleshooting.md) for deeper component-by-component checks.

## General response principles

Before changing configuration:

- confirm the affected service, environment, region, and time window;
- establish whether the application is unhealthy or only telemetry visibility is degraded;
- preserve relevant logs, traces, metrics, deployment events, and timestamps;
- avoid broad IAM, network, retention, or sampling changes during initial triage;
- prefer reversible containment actions;
- record every manual change and its rollback step;
- escalate when customer impact, data loss, security exposure, or sustained blind spots are possible.

## Runbook 1: High application error rate

### Trigger

Use this runbook when an alarm, dashboard, or trace view shows a sustained increase in application errors, failed requests, task crashes, or unsuccessful background jobs.

### First checks

1. Confirm the error-rate increase is outside the normal baseline and not caused by a dashboard or query change.
2. Identify the affected service, task revision, endpoint, operation, dependency, and availability zone where possible.
3. Check recent deployments, configuration changes, feature flags, infrastructure changes, and dependency incidents.
4. Compare error rate with request volume, latency, CPU, memory, task restarts, and saturation.
5. Search structured logs using a narrow time window and correlation identifiers.
6. Inspect representative traces to determine whether failures begin in the application or a downstream dependency.
7. Verify whether health checks and ECS service events show unhealthy or repeatedly replaced tasks.

### Likely causes

- defective application deployment or configuration change;
- unavailable or slow database, cache, queue, API, or identity provider;
- expired certificate, credential, token, or secret version;
- resource exhaustion, throttling, connection-pool exhaustion, or task instability;
- malformed input or a sudden traffic-pattern change;
- partial regional, network, DNS, or load-balancer failure;
- missing telemetry dimensions causing unrelated failures to appear combined.

### Safe containment

- pause or roll back the most recent deployment when evidence points to that change;
- disable a narrowly scoped feature flag through the approved change path;
- shift traffic only when a tested failover or routing procedure exists;
- scale within pre-approved limits when resource saturation is confirmed;
- reduce non-essential workload only through documented operational controls.

Do not suppress the alarm, increase retries globally, widen IAM permissions, or remove validation merely to reduce the visible error count.

### Validation

Confirm that:

- error rate returns toward baseline;
- latency and resource saturation recover;
- healthy-task count remains stable;
- representative requests or jobs complete successfully;
- no new data-consistency or duplicate-processing issue has appeared;
- logs, metrics, and traces continue to arrive after recovery.

### Escalate when

- customer impact is material or increasing;
- errors involve authentication, authorisation, payments, regulated data, or possible security exposure;
- rollback fails or no safe rollback exists;
- data loss, duplicate processing, or corruption is possible;
- the root cause remains unknown after the initial evidence review.

## Runbook 2: Logs missing from CloudWatch or OpenSearch

### Trigger

Use this runbook when expected application logs are absent, delayed, incomplete, or searchable in one backend but not another.

### First checks

1. Confirm the application is still running and writing useful output to `stdout` or `stderr`.
2. Check the ECS task definition log driver, stream prefix, FireLens settings, and container dependencies.
3. Verify the expected CloudWatch log group, region, stream, and retention configuration.
4. Inspect the FireLens or Fluent Bit sidecar logs for startup, authentication, buffer, retry, or delivery errors.
5. Compare a known test event across the application output, CloudWatch stream, and OpenSearch index.
6. Check whether a deployment changed service names, task families, index patterns, or routing configuration.
7. Verify that log timestamps and the search time zone are aligned.

### Likely causes

- application no longer writes to standard output;
- wrong log group, region, stream prefix, or task-definition reference;
- FireLens sidecar not running or not ready before the application emits logs;
- invalid Fluent Bit destination, parser, authentication, TLS, or index configuration;
- task execution role or task role missing a specific required permission;
- backend rejection caused by document size, mapping conflicts, rate limits, or unavailable storage;
- buffering, retry backoff, or network interruption causing delayed delivery;
- search query, index alias, or time-window mismatch.

### Safe containment

- preserve task and sidecar logs before replacing tasks;
- restore the last known-good routing configuration if a recent deployment introduced the gap;
- keep CloudWatch as the temporary searchable source when OpenSearch ingestion alone is affected;
- send one non-sensitive synthetic test record to validate the path;
- increase diagnostic logging only briefly, with an owner and removal time.

Do not log secrets, request bodies, customer records, tokens, or complete headers to compensate for missing telemetry.

### Validation

Confirm that:

- a synthetic record appears in each expected destination;
- the application and routing containers remain healthy;
- backlog or buffered-record counts decrease;
- no duplicate log stream or index is being populated instead;
- retention, encryption, and access controls remain unchanged unless explicitly approved.

### Escalate when

- the logging blind spot affects incident investigation, security monitoring, audit evidence, or regulated records;
- buffer exhaustion or dropped records may have caused permanent data loss;
- the failure requires IAM, KMS, VPC, certificate, or production backend changes;
- logs contain or may have exposed sensitive information.

## Runbook 3: OpenTelemetry Collector unhealthy or unavailable

### Trigger

Use this runbook when the collector task repeatedly restarts, fails health checks, reports dropped telemetry, or stops exporting metrics and traces.

### First checks

1. Review ECS service events, stopped-task reasons, exit codes, CPU, memory, and restart frequency.
2. Inspect collector logs for configuration parsing, receiver binding, memory limiter, queue, exporter, TLS, authentication, and timeout errors.
3. Validate that application exporter endpoints, protocols, and ports match the collector receivers.
4. Confirm that the active collector configuration contains the expected receivers, processors, exporters, and service pipelines.
5. Check downstream backend availability and network reachability.
6. Compare the failure time with deployments, task-size changes, certificate rotation, or backend maintenance.
7. Determine whether telemetry is being buffered, sampled, retried, or dropped.

### Likely causes

- invalid collector configuration or unsupported component setting;
- receiver/exporter protocol or endpoint mismatch;
- memory limit too low for current batch size or telemetry volume;
- backend latency causing queue growth and exporter timeouts;
- DNS, TLS, authentication, proxy, or security-group failure;
- excessive telemetry cardinality or payload size;
- incompatible collector image or configuration introduced by a deployment.

### Safe containment

- roll back to the last known-good collector image and configuration;
- reduce non-essential telemetry at the source through an approved, temporary change;
- lower batch size or queue pressure only when the operational trade-off is understood;
- keep application availability independent from collector health where architecture permits;
- preserve collector logs and stopped-task metadata before replacement.

Do not disable memory protection, TLS verification, authentication, or all sampling controls as a quick fix.

### Validation

Confirm that:

- collector tasks remain stable for the agreed observation window;
- receiver, processor, queue, and exporter error counters return to normal;
- new test metrics and traces reach the intended backend;
- application latency and resource usage remain acceptable;
- telemetry volume and cardinality do not immediately recreate the failure.

### Escalate when

- application availability depends on collector health;
- telemetry loss affects security detection, regulated monitoring, or an active incident;
- configuration rollback does not stabilise the collector;
- the fix requires network, certificate, secret, or backend-capacity changes;
- sustained dropped telemetry prevents reliable service assessment.

## Runbook 4: OpenSearch indexing delay or rejection

### Trigger

Use this runbook when logs reach the routing layer but appear late, remain unsearchable, or are rejected by OpenSearch.

### First checks

1. Confirm the events left ECS by checking FireLens or Fluent Bit delivery and retry logs.
2. Check OpenSearch cluster health, free storage, JVM pressure, indexing latency, rejected requests, thread-pool queues, and shard state.
3. Review index aliases, templates, mappings, lifecycle policies, rollover state, and write-block settings.
4. Inspect rejection messages for mapping conflicts, invalid field types, oversized documents, authentication failures, or rate limits.
5. Compare ingestion volume with the expected baseline and recent application or logging changes.
6. Check whether high-cardinality fields or unexpected payload growth increased index pressure.
7. Verify the event timestamps, target index, environment prefix, and search time range.

### Likely causes

- exhausted storage or a cluster write block;
- unhealthy or relocating shards;
- mapping conflict after an application log-format change;
- indexing throughput exceeding cluster or shard capacity;
- excessive shard count, document size, field count, or high-cardinality data;
- failed rollover or index lifecycle policy;
- backend authentication, TLS, or network interruption;
- retry backlog following a temporary backend outage.

### Safe containment

- reduce non-essential debug logging through an approved temporary change;
- route or retain logs in CloudWatch while OpenSearch recovers;
- restore a compatible log format when a recent application change caused mapping rejection;
- apply documented rollover or storage-recovery procedures only with the appropriate owner;
- preserve rejected-event samples without including sensitive payloads.

Do not delete indexes, disable lifecycle controls, change mappings broadly, or increase cluster capacity without an approved recovery plan.

### Validation

Confirm that:

- indexing latency and rejection rates return to acceptable levels;
- new test events are searchable in the intended index;
- backlog and retry queues drain without causing duplicates or renewed saturation;
- cluster health, storage headroom, JVM pressure, and shard state remain stable;
- index mappings and retention behaviour still meet the intended design.

### Escalate when

- data loss or prolonged search unavailability is possible;
- storage, shard, mapping, or lifecycle changes require specialist ownership;
- the cluster remains unhealthy after reducing ingestion pressure;
- security or audit logs are affected;
- recovery requires index deletion, snapshot restore, capacity expansion, or access-control changes.

## Incident handoff template

Record the following before handing the incident to another team or responder:

```text
Incident:
Start time and timezone:
Affected service/environment/region:
Customer or operational impact:
Primary alert or symptom:
Recent relevant change:
Evidence reviewed:
Current working theory:
Containment actions taken:
Validation performed:
Outstanding risk or blind spot:
Next owner and escalation path:
Rollback required:
```

A runbook supports consistent response, but it does not replace service-specific alarms, tested recovery procedures, access controls, change approval, or incident command.