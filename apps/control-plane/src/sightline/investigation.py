def investigate(request) -> dict:
    facts = [f"Reported symptom: {s}" for s in request.symptoms]
    facts.extend(f"Provided evidence: {e}" for e in request.evidence)
    text = " ".join(request.symptoms).lower()
    hypotheses, checks = [], ["Compare candidate and baseline with the same workload.", "Inspect correlated traces for the affected service and time window.", "Reproduce the issue before changing production."]
    if "latency" in text or "timeout" in text:
        hypotheses.append("Latency/timeout regression is plausible but not confirmed.")
        checks.append("Inspect p95/p99 latency and downstream dependency spans.")
    if "error" in text or "fail" in text:
        hypotheses.append("An increased failure rate may contribute; verify against event counts.")
        checks.append("Group errors by release, dependency, and error class.")
    if not hypotheses: hypotheses.append("Insufficient evidence to prioritize a root-cause hypothesis.")
    return {"service": request.service, "version": request.version, "observed_facts": facts, "hypotheses": hypotheses, "recommended_checks": checks, "human_review_required": True}
