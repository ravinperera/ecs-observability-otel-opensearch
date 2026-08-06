# Security Policy

This repository is a public reference pattern for ECS observability. It contains example task definitions, IAM policies, telemetry configuration, Terraform snippets, and operational guidance. It does not operate a hosted service and must be adapted and reviewed before production use.

## Report Security Concerns Privately

Do not include exploit details, credentials, account identifiers, internal endpoints, customer data, production logs, trace payloads, or sensitive screenshots in a public issue or pull request.

Use GitHub's **Report a vulnerability** option in the repository Security tab when it is available. If private vulnerability reporting is not available, open a minimal public issue titled `Private security contact requested` that contains only:

- the affected repository area;
- a high-level impact category;
- confirmation that you have not published sensitive evidence.

Wait for the repository owner to arrange a safer channel before sharing reproduction details or evidence.

## Accidental Exposure

If a credential, token, cookie, private endpoint, customer identifier, or sensitive telemetry sample is committed or posted:

1. Revoke or rotate the affected secret immediately; deleting the text alone is not sufficient.
2. Remove the exposed value from the current branch or discussion.
3. Assess whether repository history, workflow logs, caches, forks, or downloaded artifacts also contain it.
4. Avoid copying the sensitive value into a new issue, pull request, or remediation note.
5. Record only sanitised containment and follow-up actions publicly.

## In Scope

Security concerns related to this repository include:

- example IAM permissions that are broader than documented;
- configurations that could expose or mishandle telemetry;
- examples that encourage credential storage or unsafe transport;
- scripts or workflows that unexpectedly access secrets or external services;
- documentation that materially misrepresents a security boundary.

## Out of Scope

Vulnerabilities in AWS, OpenSearch, Fluent Bit, OpenTelemetry, Terraform, GitHub Actions, or other third-party products should be reported to the relevant vendor. General production hardening questions and environment-specific design reviews are not vulnerability reports.

## Safe Evidence

Use synthetic or redacted examples. Replace account IDs, role ARNs, hostnames, index names, trace attributes, user identifiers, and payload values with obvious placeholders. Share the smallest evidence needed to explain the concern.
