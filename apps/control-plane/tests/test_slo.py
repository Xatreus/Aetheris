import pytest
from pydantic import ValidationError

from sightline.slo import SLOEvaluationRequest, evaluate_slo


def make_request(**overrides):
    values = {
        "service": "checkout-agent",
        "window_hours": 24,
        "total_requests": 100_000,
        "failed_requests": 10,
        "target_availability": 0.999,
    }
    values.update(overrides)
    return SLOEvaluationRequest(**values)


def test_slo_reports_healthy_window_and_remaining_budget():
    result = evaluate_slo(make_request())
    assert result.status == "healthy"
    assert result.observed_availability == pytest.approx(0.9999)
    assert result.error_budget_remaining_percent == pytest.approx(90.0)
    assert result.burn_rate == pytest.approx(0.1)


def test_slo_breach_when_failures_exceed_budget():
    result = evaluate_slo(make_request(failed_requests=150))
    assert result.status == "breached"
    assert result.error_budget_consumed_percent == pytest.approx(150.0)
    assert result.error_budget_remaining_percent == 0.0


def test_slo_marks_low_remaining_budget_at_risk():
    result = evaluate_slo(make_request(failed_requests=80))
    assert result.status == "at_risk"
    assert result.error_budget_remaining_percent == pytest.approx(20.0)


def test_slo_marks_exact_burn_threshold_at_risk():
    result = evaluate_slo(make_request(failed_requests=200))
    assert result.status == "breached"


def test_slo_rejects_failure_count_greater_than_total():
    with pytest.raises(ValidationError):
        make_request(failed_requests=100_001)


def test_slo_rejects_availability_objective_of_one():
    with pytest.raises(ValidationError):
        make_request(target_availability=1.0)


def test_zero_failures_have_zero_burn_rate():
    result = evaluate_slo(make_request(failed_requests=0))
    assert result.status == "healthy"
    assert result.burn_rate == 0
    assert result.error_budget_consumed_percent == 0
