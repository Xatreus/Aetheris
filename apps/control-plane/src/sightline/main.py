from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from .db import init_db, save_event, SessionLocal
from .investigation import investigate
from .policy import DEFAULT_POLICY, evaluate_release
from .schemas import InvestigationRequest, ReliabilityEvent, ReleaseEvaluationRequest
from .slo import SLOEvaluationRequest, evaluate_slo
@asynccontextmanager
async def lifespan(app):
    init_db(); yield
app = FastAPI(title="Aetheris Control Plane", version="0.1.0", description="Evidence-based reliability engineering for AI applications.", lifespan=lifespan)
@app.get("/health")
def health(): return {"status":"ok", "service":"aetheris-control-plane"}
@app.get("/ready")
def ready():
    try:
        with SessionLocal() as session: session.execute(text("SELECT 1"))
        return {"status":"ready", "database":"reachable"}
    except Exception as exc: raise HTTPException(status_code=503, detail="database unavailable") from exc
@app.get("/v1/policies")
def policies(): return {"active_policy": DEFAULT_POLICY.model_dump(), "policy_version":"default-v1"}
@app.post("/v1/events", status_code=201)
def ingest_event(event: ReliabilityEvent):
    try: return {"accepted":True, "event_id":save_event(event)}
    except Exception as exc: raise HTTPException(status_code=503, detail="event persistence failed") from exc
@app.post("/v1/releases/evaluate")
def release_evaluation(request: ReleaseEvaluationRequest): return evaluate_release(request)
@app.post("/v1/incidents/investigate")
def incident_investigation(request: InvestigationRequest): return investigate(request)
@app.post("/v1/slo/evaluate")
def slo_evaluation(request: SLOEvaluationRequest): return evaluate_slo(request)
