"""Deterministic SLO and error-budget calculations.

This module intentionally does not use an LLM to make SLO decisions.
The caller supplies an aggregated measurement window; production ingestion and
window aggregation are separate responsibilities.
"""
from pydantic import BaseModel, ConfigDict, Field, model_validator

# Percentages are reported to this precision to avoid binary-float noise
# changing threshold decisions at exact policy boundaries.
_PERCENT_PRECISION = 8


class SLOEvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service: str = Field(min_length=1, max_length=120)
    window_hours: int = Field(ge=1, le=24 * 90)
    total_requests: int = Field(ge=1, le=100_000_000_000)
    failed_requests: int = Field(ge=0, le=100_000_000_000)
    target_availability: float = Field(gt=0, lt=1, description="Availability objective, e.g. 0.999")

    @model_validator(mode="after")
    def failures_cannot_exceed_requests(self):
        if self.failed_requests > self.total_requests:
            raise ValueError("failed_requests cannot exceed total_requests")
        return self


class SLOEvaluationResponse(BaseModel):
    service: str
    window_hours: int
    target_availability: float
    observed_availability: float
    observed_error_rate: float
    allowed_error_rate: float
    allowed_failures: float
    observed_failures: int
    error_budget_consumed_percent: float
    error_budget_remaining_percent: float
    burn_rate: float
    status: str
    explanation: list[str]


def evaluate_slo(request: SLOEvaluationRequest) -> SLOEvaluationResponse:
    """Evaluate an availability SLO from a single aggregated measurement window."""
    total = request.total_requests
    failed = request.failed_requests
    observed_error_rate = failed / total
    allowed_error_rate = 1.0 - request.target_availability
    allowed_failures = total * allowed_error_rate

    # The target is strictly below 1, so allowed_error_rate is positive.
    burn_rate = observed_error_rate / allowed_error_rate
    consumed = (failed / allowed_failures) * 100.0
    consumed = round(consumed, _PERCENT_PRECISION)
    remaining = round(max(0.0, 100.0 - consumed), _PERCENT_PRECISION)
    burn_rate = round(burn_rate, _PERCENT_PRECISION)

    if failed > allowed_failures:
        status = "breached"
        explanation = ["Observed failures exceed the error budget for this measurement window."]
    elif burn_rate >= 2.0 or remaining <= 20.0:
        status = "at_risk"
        explanation = ["The service is consuming its error budget too quickly or has 20% or less remaining."]
    else:
        status = "healthy"
        explanation = ["The measured window is within the configured availability objective."]

    return SLOEvaluationResponse(
        service=request.service,
        window_hours=request.window_hours,
        target_availability=request.target_availability,
        observed_availability=round(1.0 - observed_error_rate, _PERCENT_PRECISION),
        observed_error_rate=round(observed_error_rate, _PERCENT_PRECISION),
        allowed_error_rate=round(allowed_error_rate, _PERCENT_PRECISION),
        allowed_failures=allowed_failures,
        observed_failures=failed,
        error_budget_consumed_percent=consumed,
        error_budget_remaining_percent=remaining,
        burn_rate=burn_rate,
        status=status,
        explanation=explanation,
    )
