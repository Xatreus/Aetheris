import pytest
from pydantic import ValidationError

from sightline.policy import evaluate_release
from sightline.schemas import ReleaseEvaluationRequest


def req(**overrides):
    metrics = {
        "p95_latency_ms": 500,
        "error_rate": 0.001,
        "evaluation_score": 0.97,
        "sample_size": 100,
    }
    metrics.update(overrides)
    return ReleaseEvaluationRequest(
        service="demo-agent",
        candidate_version="2.0",
        baseline_version="1.9",
        metrics=metrics,
    )


def test_healthy_release_passes():
    assert evaluate_release(req())["decision"] == "pass"


def test_latency_regression_blocks():
    assert evaluate_release(req(p95_latency_ms=2500))["decision"] == "block"


def test_quality_regression_blocks():
    assert evaluate_release(req(evaluation_score=0.72))["decision"] == "block"


def test_small_sample_warns():
    assert evaluate_release(req(sample_size=4))["decision"] == "warn"


def test_invalid_rate_rejected():
    with pytest.raises(ValidationError):
        req(error_rate=1.4)
