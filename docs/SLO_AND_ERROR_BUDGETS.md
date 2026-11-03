# SLOs and error budgets

Aetheris now includes a deterministic availability-SLO evaluator. It accepts a caller-supplied aggregate window and computes observed availability, allowed failures, error-budget consumption, remaining budget, and burn rate.

## Endpoint

`POST /v1/slo/evaluate`

Example:

```json
{
  "service": "checkout-agent",
  "window_hours": 24,
  "total_requests": 100000,
  "failed_requests": 10,
  "target_availability": 0.999
}
```

The response includes:
- observed availability and error rate;
- the allowed error rate and number of failures for the target;
- budget consumption and remaining percentage;
- burn rate (observed error rate divided by the SLO's allowed error rate);
- a deterministic status: `healthy`, `at_risk`, or `breached`.

## Decision semantics

- `breached`: observed failures exceed the error budget calculated for the supplied window.
- `at_risk`: the burn rate is at least 2x, or 20% or less of the budget remains.
- `healthy`: neither condition above applies.

These thresholds are starter defaults, not universal SRE policy. A real service should define its SLO window, aggregation rules, alert windows, and release policy based on its user journeys and reliability objectives.

## Important limitations

This endpoint evaluates one aggregate measurement window; it does not yet ingest raw telemetry or maintain rolling windows. Its `allowed_failures` is a fractional expected budget derived from the target and request count, so a breach is evaluated against the exact mathematical threshold rather than a rounded integer. It is not a substitute for multi-window, multi-burn-rate alerting or a full SRE implementation.
