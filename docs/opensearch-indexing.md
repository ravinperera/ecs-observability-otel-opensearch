# OpenSearch Indexing

## Index Naming

Use predictable per-environment indexes:

```text
ecs-dev-sample-api
ecs-staging-sample-api
ecs-prod-sample-api
```

This helps with access control, retention, and operational searches.

## Retention

Define retention or rollover policies. Production logs usually need a different retention policy from development logs.

## Security

OpenSearch access should be restricted by IAM, network controls, or fine-grained access controls depending on the deployment model.

## Sensitive Data

Logs should not contain secrets, access tokens, passwords, or unnecessary personal data. Add filtering where possible before logs reach OpenSearch.

## Dashboards

Useful dashboards include:

- error rate by service
- request volume
- slowest endpoints
- deployment timeline
- ECS task restarts
- top exceptions
