# Aetheris
**AI reliability engineering for systems that change faster than their test suites.**

Aetheris is an early-stage AI production reliability platform: a TypeScript OpenTelemetry SDK, Python control plane, deterministic release gates, evidence-preserving incident reports, and deployment scaffolding. The name is inspired by the *recon / situational-awareness vibe* of tactical game characters, not a game character name. Check trademarks and repository-name availability before commercial use.

> **Status: development baseline, not production-ready.** Local API and policy tests are included. Cloud manifests are starters and have not been validated in a live AWS/Azure account.

## Stack and why
- **TypeScript + Node.js:** application-side instrumentation SDK.
- **OpenTelemetry:** vendor-neutral traces and telemetry.
- **Arize Phoenix (optional):** inspect LLM/agent traces; Aetheris does not rebuild its UI.
- **Evidently (planned integration):** statistical monitoring and drift checks.
- **FastAPI + Pydantic:** typed control-plane API and input validation.
- **PostgreSQL:** shared operational persistence; SQLite is the zero-setup test default.
- **LangGraph (planned milestone):** bounded, evidence-based investigation workflow; release decisions remain deterministic.
- **Docker Compose, Kubernetes, Terraform, GitHub Actions:** reproducible development, deployment, and CI.
- **AWS EKS first; Azure AKS portability later:** avoid expensive duplicate production environments.

## Architecture
```text
AI application -> TypeScript SDK -> OpenTelemetry Collector -> Phoenix (optional)
                                     |                       
                                     +-> Aetheris Control Plane (FastAPI)
                                           |-- event store (PostgreSQL/SQLite)
                                           |-- deterministic reliability policies
                                           |-- evidence-first incident report
                                           +-- CI/CD release gate (pass/warn/block)
```

## Local quick start
Requirements: Python 3.11+ (3.12 recommended).
```bash
cd apps/control-plane
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
uvicorn sightline.main:app --reload
```
Open `http://127.0.0.1:8000/docs`.

The API defaults to SQLite. Set `DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname` for PostgreSQL.

## TypeScript SDK
Requires Node.js 20+.
```bash
cd packages/ts-sdk
npm install
npm run build
```
The SDK helper creates OpenTelemetry spans and filters common sensitive attribute names. This is only defense-in-depth; do not attach prompts, completions, credentials, or customer data to telemetry.

## API
- `GET /health` — liveness.
- `GET /ready` — database readiness.
- `GET /v1/policies` — current illustrative policy.
- `POST /v1/events` — store a typed reliability event.
- `POST /v1/releases/evaluate` — deterministic release gate.
- `POST /v1/incidents/investigate` — evidence-preserving investigation report; no autonomous actions.
- `POST /v1/slo/evaluate` — deterministic availability SLO, error-budget consumption, and burn-rate evaluation (see `docs/SLO_AND_ERROR_BUDGETS.md`).

Example release request: `examples/release-evaluation.json`.

## Development principles
1. Release gates are deterministic and versioned; an LLM must not silently override policy.
2. Keep observed facts separate from hypotheses.
3. Missing or low-volume evidence should lower confidence, not imply certainty.
4. No production write actions or autonomous rollback in this baseline.
5. Treat logs, telemetry, and model output as untrusted input.

## Roadmap
- [x] Typed FastAPI control plane, event persistence, policy engine, tests
- [x] TypeScript OpenTelemetry SDK baseline
- [x] Docker and local Compose setup
- [x] Kubernetes deployment starter and cloud scaffolding
- [x] Deterministic SLO evaluation and error-budget calculations (aggregate-window input)
- [ ] Authentication, tenant isolation, rate limits, audit trail
- [ ] Validate OTLP Collector -> Phoenix pipeline end-to-end
- [ ] Evidently drift/quality integration and benchmark
- [ ] LangGraph investigation workflow with tool allowlists and human approval
- [ ] Baseline/candidate replay evaluation with false-positive/negative reporting
- [ ] AWS EKS deployment; Azure AKS portability tests
- [ ] Dependency lockfiles, container scanning, security review, and cost budgets

## Security warning
The local API has **no authentication**. Do not expose it to the public internet or send sensitive production telemetry. See `docs/THREAT_MODEL.md`.
