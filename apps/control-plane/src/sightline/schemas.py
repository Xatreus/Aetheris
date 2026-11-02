from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

class ReliabilityEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: str = Field(min_length=1, max_length=120)
    environment: str = Field(default="development", max_length=40)
    version: str = Field(min_length=1, max_length=80)
    event_type: Literal["request", "tool_call", "evaluation", "error", "custom"]
    latency_ms: float | None = Field(default=None, ge=0, le=3600000)
    success: bool | None = None
    evaluation_score: float | None = Field(default=None, ge=0, le=1)
    trace_id: str | None = Field(default=None, max_length=64)
    attributes: dict[str, str | int | float | bool] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReleaseMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")
    p95_latency_ms: float = Field(ge=0, le=3600000)
    error_rate: float = Field(ge=0, le=1)
    evaluation_score: float = Field(ge=0, le=1)
    sample_size: int = Field(default=100, ge=1, le=10000000)

class ReleaseEvaluationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: str = Field(min_length=1, max_length=120)
    candidate_version: str = Field(min_length=1, max_length=80)
    baseline_version: str = Field(min_length=1, max_length=80)
    metrics: ReleaseMetrics

class Policy(BaseModel):
    name: str
    max_p95_latency_ms: float
    max_error_rate: float
    min_evaluation_score: float
    min_sample_size: int = 20

class CheckResult(BaseModel):
    name: str
    status: Literal["pass", "warn", "fail"]
    observed: float | int
    threshold: float | int
    message: str

class InvestigationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    service: str = Field(min_length=1, max_length=120)
    version: str = Field(min_length=1, max_length=80)
    symptoms: list[str] = Field(min_length=1, max_length=20)
    evidence: list[str] = Field(default_factory=list, max_length=30)
