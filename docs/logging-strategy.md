# Logging Strategy

## Application Logs

Applications should write structured JSON logs to stdout and stderr. The container runtime and FireLens can then route those logs to CloudWatch Logs and OpenSearch.

## Recommended Fields

Useful fields include:

- timestamp
- level
- service
- environment
- trace_id
- request_id
- user_id where safe and appropriate
- message

Avoid logging secrets, tokens, passwords, personal data, or full request payloads unless explicitly approved and protected.

## CloudWatch Logs

CloudWatch Logs is useful for operational troubleshooting and AWS-native integrations. Set retention explicitly so logs do not grow forever.

## OpenSearch

OpenSearch is useful for searching, dashboards, and operational investigations. Use per-environment indexes, for example:

```text
ecs-dev-sample-api
ecs-staging-sample-api
ecs-prod-sample-api
```
