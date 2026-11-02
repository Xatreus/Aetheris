from .schemas import Policy, ReleaseEvaluationRequest

DEFAULT_POLICY = Policy(name="balanced-default", max_p95_latency_ms=2000, max_error_rate=0.02, min_evaluation_score=0.90, min_sample_size=30)

def evaluate_release(request: ReleaseEvaluationRequest, policy: Policy = DEFAULT_POLICY) -> dict:
    m = request.metrics
    checks = []
    rules = [
        ("p95_latency", m.p95_latency_ms, policy.max_p95_latency_ms, m.p95_latency_ms <= policy.max_p95_latency_ms, "p95 latency"),
        ("error_rate", m.error_rate, policy.max_error_rate, m.error_rate <= policy.max_error_rate, "error rate"),
        ("evaluation_score", m.evaluation_score, policy.min_evaluation_score, m.evaluation_score >= policy.min_evaluation_score, "evaluation score"),
    ]
    for name, observed, threshold, passed, label in rules:
        checks.append({"name": name, "status": "pass" if passed else "fail", "observed": observed, "threshold": threshold, "message": f"{label} meets policy" if passed else f"{label} violates policy"})
    if m.sample_size < policy.min_sample_size:
        checks.append({"name": "sample_size", "status": "warn", "observed": m.sample_size, "threshold": policy.min_sample_size, "message": "sample size is too small for a confident release decision"})
    failed = [c for c in checks if c["status"] == "fail"]
    warned = [c for c in checks if c["status"] == "warn"]
    decision = "block" if failed else "warn" if warned else "pass"
    rationale = [c["message"] for c in checks if c["status"] != "pass"] or ["All configured reliability checks passed."]
    return {"service": request.service, "candidate_version": request.candidate_version, "baseline_version": request.baseline_version, "decision": decision, "checks": checks, "rationale": rationale, "policy_version": "default-v1"}
