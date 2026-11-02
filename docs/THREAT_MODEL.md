# Initial threat model
## Assets
Telemetry metadata, trace IDs, release policies, evaluation results, database credentials, cloud identities, release decision integrity.
## Trust boundaries
Instrumented app -> SDK -> collector; collector -> observability backend; CI -> release API; API -> database; future agent -> tools.
## Risks and current controls
- Sensitive telemetry: SDK filters common sensitive attribute names; collector deletes selected fields. This is not complete DLP.
- Invalid inputs: typed Pydantic models and bounds.
- Untrusted logs: investigation treats them as evidence, not instructions; no tools exposed.
- Wrong release decisions: deterministic policy and tests; sample-size warning.
- Unauthorized API access: authentication is not implemented; never expose publicly.
- Secrets: Compose credentials are local-only; production secret delivery is not configured.
- Supply chain: dependencies are not fully locked; add lockfiles and vulnerability scanning before release.
## Before production
Authentication, authorization, tenant isolation, rate limiting, audit logs, secure secret delivery, dependency lockfiles, container scanning, retention policy, incident response, load tests and threat-model review.
