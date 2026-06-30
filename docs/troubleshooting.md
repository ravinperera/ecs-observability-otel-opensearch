# Troubleshooting Guide

Use this guide when an ECS workload is running but logs, metrics, or traces are missing, delayed, duplicated, or hard to search.

## 1. Confirm The Application Is Producing Useful Logs

Start with the application container before looking at routing layers.

Check that:

- The application writes structured logs to stdout or stderr
- Log records include a timestamp, service name, environment, and correlation identifier where possible
- Health checks, startup messages, and request errors are visible in the task logs
- Sensitive values are not written into logs

If application logs are missing locally, FireLens, CloudWatch, and OpenSearch will not be able to recover them later in the pipeline.

## 2. Check CloudWatch Log Groups

CloudWatch Logs is usually the first place to validate whether the ECS task is emitting output.

Check that:

- The expected log group exists
- The ECS task execution role can create log streams and put log events
- The stream prefix matches the task definition
- Retention is set deliberately rather than left unlimited by accident
- The log region matches the ECS cluster region

A common failure is changing the service or family name without updating the log group or stream prefix references.

## 3. Check FireLens / Fluent Bit Routing

If CloudWatch has logs but OpenSearch does not, focus on the FireLens or Fluent Bit path.

Check that:

- The FireLens sidecar starts successfully
- The application container uses the intended log driver
- The Fluent Bit configuration references the expected host, port, index pattern, and authentication method
- Buffer limits are sized for expected bursts
- Retry settings are suitable for temporary backend failures

Prefer a small test message before assuming the full workload is broken.

## 4. Check The OpenTelemetry Collector

For metrics and traces, validate the collector separately from the application.

Check that:

- The collector task starts and remains healthy
- Receiver ports match the application exporter configuration
- Pipelines include the expected receivers, processors, and exporters
- Batch and memory limiter processors are configured for the task size
- Collector logs do not show exporter errors or dropped telemetry

If traces are missing but metrics work, compare receiver protocol, endpoint, and sampling configuration.

## 5. Check Backend Delivery

When telemetry leaves ECS but does not appear in the backend, validate delivery and indexing.

Check that:

- Security groups and routing allow the ECS task to reach the backend endpoint
- TLS and authentication settings match the backend requirement
- Index names include the expected environment or service prefix
- Index templates and mappings accept the fields being sent
- The backend is not rejecting documents due to size, type mismatch, or rate limits

Use backend rejection logs where available. They often explain why data is not searchable.

## 6. Check IAM Permissions

Keep permissions narrow, but make sure the roles have the specific actions they need.

Review:

- ECS task execution role permissions for pulling images and writing logs
- Task role permissions used by collectors or exporters
- CloudWatch Logs permissions for log groups and streams
- Secrets access if credentials are loaded at runtime
- KMS permissions if log groups, secrets, or backend credentials are encrypted

Avoid solving observability issues by adding broad administrative policies.

## 7. Check Retention And Cost Controls

Observability pipelines can become expensive if retention and indexing are left open-ended.

Check that:

- CloudWatch retention is defined per environment
- OpenSearch index lifecycle rules are documented
- High-cardinality fields are reviewed before indexing
- Debug logs are temporary and removed after diagnosis
- Sampling decisions are explicit for traces

## Quick Triage Order

1. Application stdout/stderr
2. CloudWatch log stream
3. FireLens / Fluent Bit sidecar logs
4. OpenTelemetry Collector logs
5. Network path to backend
6. Backend rejection or indexing logs
7. IAM and encryption permissions

This order keeps the investigation close to the source before moving into routing and backend configuration.
