# Sensitive Telemetry Handling

Logs, metrics, and traces often cross service and account boundaries. Treat telemetry as production data and prevent sensitive values from entering the pipeline whenever possible.

## Data to exclude by default

Do not emit:

- passwords, API keys, access tokens, cookies, or authorization headers
- private keys, connection strings, or signed URLs
- full request or response bodies
- payment-card, health, identity, or other regulated data
- personal identifiers unless an approved operational use case requires them
- database queries containing customer-supplied values

Prefer an allow-list of approved attributes over attempting to block every unsafe field.

## Application controls

- Log stable event names and identifiers rather than raw objects.
- Replace user-facing identifiers with non-reversible, purpose-specific values where correlation is required.
- Redact values before they reach stdout; downstream filtering is a secondary safeguard.
- Configure frameworks to suppress headers, query strings, and bodies by default.
- Ensure exception handlers do not serialize request context or environment variables.
- Add automated tests for representative secret and personal-data patterns.

## Collector and routing controls

- Use OpenTelemetry processors or Fluent Bit filters to remove prohibited attributes.
- Drop entire records when redaction cannot reliably make them safe.
- Keep processor configuration in version control and review changes like application code.
- Fail safely: a broken redaction rule should not silently route unfiltered data to another destination.
- Avoid duplicating telemetry across destinations without a documented need and retention owner.

## Access and encryption

- Encrypt telemetry in transit and at rest.
- Use narrowly scoped task roles and separate producer, collector, and analyst permissions.
- Restrict OpenSearch index access by environment and operational role.
- Record administrative access and configuration changes.
- Use private networking or controlled egress where practical.
- Do not place credentials directly in task definitions, collector files, or repository examples.

## Retention and deletion

Set retention according to the shortest operational and legal requirement that applies. Document:

- the owner of each log group, index, metric namespace, and trace store
- retention by environment and data class
- index lifecycle and snapshot expiry settings
- deletion procedures for accidental sensitive-data ingestion
- any legal hold or audit exception

Backups and snapshots must not outlive the approved retention period without an explicit exception.

## Detection and response

Monitor for common secret formats and unexpected fields, but do not rely on scanners as the primary control. When sensitive data is detected:

1. Stop or filter the source.
2. Revoke or rotate exposed credentials immediately.
3. Restrict access to the affected telemetry store.
4. Identify every destination, replica, export, snapshot, and downstream consumer.
5. Delete data according to the incident and legal process.
6. Preserve only the evidence required for investigation.
7. Add a regression test or policy check before restoring the signal.

Do not copy exposed values into tickets, chat, or incident documents.

## Review checklist

Before adding or changing telemetry, confirm:

- [ ] The event has a named operational purpose and owner.
- [ ] Emitted fields use an allow-list.
- [ ] Secrets, headers, bodies, and personal data are excluded.
- [ ] Redaction is tested with realistic failure cases.
- [ ] Collector and routing filters are reviewed.
- [ ] Access is least privilege and separated by environment.
- [ ] Encryption, retention, deletion, and backup expiry are defined.
- [ ] An accidental-ingestion response procedure exists.

Telemetry that cannot satisfy these controls should not be enabled in production.
