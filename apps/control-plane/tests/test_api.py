from fastapi.testclient import TestClient

from sightline.main import app


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_release_gate():
    payload = {
        "service": "demo",
        "candidate_version": "1.1",
        "baseline_version": "1.0",
        "metrics": {
            "p95_latency_ms": 300,
            "error_rate": 0.001,
            "evaluation_score": 0.98,
            "sample_size": 100,
        },
    }
    with TestClient(app) as client:
        response = client.post("/v1/releases/evaluate", json=payload)
    assert response.status_code == 200
    assert response.json()["decision"] == "pass"


def test_investigation_requires_review():
    payload = {
        "service": "demo",
        "version": "1.2",
        "symptoms": ["timeouts increased after release"],
        "evidence": ["slow database span"],
    }
    with TestClient(app) as client:
        response = client.post("/v1/incidents/investigate", json=payload)
    assert response.status_code == 200
    assert response.json()["human_review_required"] is True
