import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.config import settings

@dataclass
class StepTrace:
    step_id: str
    name: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    thinking_tokens: int
    latency_ms: float
    cost_usd: float
    timestamp: str
    status: str
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RunTrace:
    trace_id: str
    task: str
    effort: str
    start_time: str
    end_time: Optional[str] = None
    total_latency_ms: float = 0.0
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_thinking_tokens: int = 0
    total_cost_usd: float = 0.0
    steps: List[StepTrace] = field(default_factory=list)
    success: bool = True
    error_message: Optional[str] = None

class TelemetryService:
    def __init__(self):
        self.active_runs: Dict[str, RunTrace] = {}
        self.completed_runs: List[RunTrace] = []

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Pure code deterministic cost calculation in USD."""
        if "pro" in model.lower():
            p_rate = settings.pro_prompt_cost_per_m
            c_rate = settings.pro_completion_cost_per_m
        else:
            p_rate = settings.flash_prompt_cost_per_m
            c_rate = settings.flash_completion_cost_per_m

        cost = (prompt_tokens / 1_000_000.0) * p_rate + (completion_tokens / 1_000_000.0) * c_rate
        return round(cost, 6)

    def start_run(self, task: str, effort: str = "standard") -> RunTrace:
        trace_id = f"trace-{uuid.uuid4().hex[:12]}"
        run = RunTrace(
            trace_id=trace_id,
            task=task,
            effort=effort,
            start_time=datetime.now(timezone.utc).isoformat(),
        )
        self.active_runs[trace_id] = run
        return run

    def record_step(
        self,
        trace_id: str,
        name: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        thinking_tokens: int,
        latency_ms: float,
        status: str = "success",
        details: Optional[Dict[str, Any]] = None,
    ) -> StepTrace:
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        step = StepTrace(
            step_id=f"step-{uuid.uuid4().hex[:8]}",
            name=name,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            thinking_tokens=thinking_tokens,
            latency_ms=round(latency_ms, 2),
            cost_usd=cost,
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status,
            details=details or {},
        )

        if trace_id in self.active_runs:
            run = self.active_runs[trace_id]
            run.steps.append(step)
            run.total_prompt_tokens += prompt_tokens
            run.total_completion_tokens += completion_tokens
            run.total_thinking_tokens += thinking_tokens
            run.total_latency_ms += latency_ms
            run.total_cost_usd += cost

        return step

    def end_run(self, trace_id: str, success: bool = True, error_message: Optional[str] = None) -> Optional[RunTrace]:
        if trace_id not in self.active_runs:
            return None
        run = self.active_runs.pop(trace_id)
        run.end_time = datetime.now(timezone.utc).isoformat()
        run.success = success
        run.error_message = error_message
        self.completed_runs.append(run)
        # Keep last 100 runs in memory for telemetry inspection
        if len(self.completed_runs) > 100:
            self.completed_runs.pop(0)
        return run

    def get_recent_traces(self, limit: int = 20) -> List[Dict[str, Any]]:
        traces = list(reversed(self.completed_runs[-limit:]))
        return [
            {
                "trace_id": r.trace_id,
                "task": r.task,
                "effort": r.effort,
                "start_time": r.start_time,
                "end_time": r.end_time,
                "latency_ms": round(r.total_latency_ms, 2),
                "tokens": {
                    "prompt": r.total_prompt_tokens,
                    "completion": r.total_completion_tokens,
                    "thinking": r.total_thinking_tokens,
                    "total": r.total_prompt_tokens + r.total_completion_tokens + r.total_thinking_tokens,
                },
                "cost_usd": round(r.total_cost_usd, 6),
                "success": r.success,
                "steps_count": len(r.steps),
                "steps": [
                    {
                        "name": s.name,
                        "model": s.model,
                        "tokens": s.prompt_tokens + s.completion_tokens + s.thinking_tokens,
                        "latency_ms": s.latency_ms,
                        "cost_usd": s.cost_usd,
                        "status": s.status,
                        "details": s.details,
                    }
                    for s in r.steps
                ],
            }
            for r in traces
        ]

telemetry = TelemetryService()
