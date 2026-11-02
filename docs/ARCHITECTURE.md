# Architecture decisions
1. Release decisions are deterministic policy evaluations; LLMs cannot override them.
2. Integrate OpenTelemetry and Phoenix rather than rebuilding tracing UIs. Evidently is a planned statistical monitoring integration.
3. SQLite supports tests and local iteration; PostgreSQL is intended for shared environments.
4. AWS EKS is first; Azure AKS portability follows after validation.
5. Investigation is advisory. No production write actions in the initial version.
6. Next decisions: authentication/tenant isolation, event retention, policy audit trail, statistical baseline comparisons, LangGraph tool allowlist and human approval, sampling/cardinality limits.
