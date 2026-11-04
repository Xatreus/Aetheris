# Aetheris SDK runtime metrics

The TypeScript SDK emits OpenTelemetry spans and application-level metrics for each call to observeOperation.

| Instrument | Type | Meaning |
|---|---|---|
| aetheris.operations | Counter | Total number of observed operations |
| aetheris.operation.errors | Counter | Number of observed operations that threw an error |
| aetheris.operation.duration | Histogram (ms) | Operation duration distribution |

Metrics use bounded dimensions supplied by the SDK: service name, deployment environment, and operation name. Arbitrary user attributes are attached only to spans, not metric labels, to reduce accidental high-cardinality metric series.

## Export

The SDK exports OTLP/HTTP traces and metrics to the OpenTelemetry Collector.

- OTEL_EXPORTER_OTLP_ENDPOINT: base endpoint; defaults to http://localhost:4318.
- OTEL_EXPORTER_OTLP_TRACES_ENDPOINT: optional trace endpoint override.
- OTEL_EXPORTER_OTLP_METRICS_ENDPOINT: optional metric endpoint override.

The Collector sends traces to optional Phoenix and writes both traces and metrics to its debug exporter. Metrics are intentionally not sent to Phoenix in this starter configuration.

## Run locally

From the repository root:

    docker compose --profile observability up -d

Then:

    cd packages/ts-sdk
    npm install
    npm run build
    node dist/example.js

Inspect Collector output with:

    docker compose logs -f otel-collector

Phoenix is available at http://localhost:6006.

## Privacy and cardinality

The SDK filters common sensitive attribute names, but this is defense-in-depth, not a guarantee that arbitrary values are safe. Never attach prompts, completions, credentials, personal data, or raw request/response bodies to telemetry. Keep operation names bounded and stable; do not use user IDs, request IDs, or other per-request values as metric dimensions.

The Collector redacts selected attributes, but a production deployment must define a data classification policy and validate redaction against the actual instrumentation used by each service.
