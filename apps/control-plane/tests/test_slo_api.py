from fastapi.testclient import TestClient

from sightline.main import app


def test_slo_evaluation_endpoint():
    payload = {
        "service": "checkout-agent",
        "window_hours": 24,
        "total_requests": 100_000,
        "failed_requests": 10,
        "target_availability": 0.999,
    }
    with TestClient(app) as client:
        response = client.post("/v1/slo/evaluate", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["observed_availability"] == 0.9999
    assert body["error_budget_consumed_percent"] == 10.0


def test_slo_endpoint_rejects_impossible_failure_count():
    payload = {
        "service": "checkout-agent",
        "window_hours": 24,
        "total_requests": 100,
        "failed_requests": 101,
        "target_availability": 0.999,
    }
    with TestClient(app) as client:
        response = client.post("/v1/slo/evaluate", json=payload)

    assert response.status_code == 422
