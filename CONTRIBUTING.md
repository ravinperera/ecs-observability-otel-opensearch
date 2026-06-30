# Contributing

Thank you for improving this ECS observability reference. This repository is intended to stay practical, generic, and safe to reuse as a portfolio-quality example.

## What Makes a Good Change

Good contributions usually improve one of these areas:

- ECS task definition examples
- OpenTelemetry Collector configuration
- Fluent Bit / FireLens routing examples
- Terraform examples for log groups, IAM, or variables
- Documentation that explains operational trade-offs
- Security, retention, or troubleshooting guidance

Keep changes small and focused. A pull request should be easy to review without needing access to a real AWS account.

## Safety Expectations

Before opening a pull request, check that the change:

- Uses placeholder names instead of real account IDs, ARNs, domains, hosts, or customer data
- Does not include credentials, tokens, production logs, or private endpoints
- Keeps IAM permissions narrow and explains why each permission is needed
- Avoids logging secrets, request bodies, authentication headers, or sensitive payloads
- Preserves sensible retention and indexing defaults
- Notes any production caveats clearly in the relevant document

## Documentation Style

Use direct, practical language. Prefer examples that help a DevOps or platform engineer understand why the pattern exists and when to adapt it.

When adding a new document, link it from the README so visitors can find it quickly.

## Review Checklist

Before merging, confirm that:

- The change is generic and safe for a public repository
- File paths in the README still match the repository structure
- JSON, YAML, Terraform, and Markdown examples remain readable
- Any operational assumptions are documented
- The change improves the repository rather than only adding activity
