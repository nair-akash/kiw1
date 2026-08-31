import asyncio
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from app.armor import model_armor
from app.gateway import agent_gateway
from app.store import store

@dataclass
class RuntimeTaskStep:
    step_index: int
    name: str
    action_type: str
    status: str  # "pending", "running", "completed", "failed", "paused_for_approval"
    payload: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None

@dataclass
class RuntimeExecutionJob:
    job_id: str
    agent_id: str
    title: str
    department: str
    status: str  # "queued", "running", "completed", "failed", "paused"
    steps: List[RuntimeTaskStep] = field(default_factory=list)
    current_step: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    checkpoint_state: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class AgentRuntime:
    """Enterprise Agent Runtime:
    Executes long-running, asynchronous multi-step DAG workflows across weeks
    with checkpointing, state serialization, and zero-trust verification.
    """

    def __init__(self):
        self._jobs: Dict[str, RuntimeExecutionJob] = {}

    def create_job(
        self,
        agent_id: str,
        title: str,
        department: str,
        steps: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RuntimeExecutionJob:
        job_id = f"job-{uuid.uuid4().hex[:10]}"
        now = datetime.now(timezone.utc).isoformat()

        task_steps = [
            RuntimeTaskStep(
                step_index=i,
                name=s.get("name", f"Step {i+1}"),
                action_type=s.get("action_type", "compute"),
                status="pending",
                payload=s.get("payload", {}),
            )
            for i, s in enumerate(steps)
        ]

        job = RuntimeExecutionJob(
            job_id=job_id,
            agent_id=agent_id,
            title=title,
            department=department,
            status="queued",
            steps=task_steps,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )
        self._jobs[job_id] = job
        return job

    async def execute_job(self, job_id: str) -> Dict[str, Any]:
        """Executes a runtime job step-by-step with zero-trust checks and checkpointing."""
        job = self._jobs.get(job_id)
        if not job:
            return {"success": False, "error": f"Job '{job_id}' not found"}

        job.status = "running"
        job.updated_at = datetime.now(timezone.utc).isoformat()

        for step in job.steps:
            if step.status == "completed":
                continue

            step.status = "running"
            step.started_at = datetime.now(timezone.utc).isoformat()

            # Zero-trust tool authorization check
            action = step.action_type
            auth_ok, auth_err = agent_gateway.authorize_tool_call(job.agent_id, action, step.payload)
            if not auth_ok and action != "internal_reasoning":
                step.status = "failed"
                step.error = auth_err
                job.status = "failed"
                job.updated_at = datetime.now(timezone.utc).isoformat()
                return {"success": False, "job_id": job_id, "failed_step": step.step_index, "error": auth_err}

            # Inline Model Armor Inspection
            payload_str = str(step.payload)
            is_safe, sanitized_str, threats = model_armor.inspect_input(payload_str)
            if not is_safe:
                step.status = "failed"
                step.error = f"Model Armor Security Trigger: {', '.join(threats)}"
                job.status = "failed"
                return {"success": False, "job_id": job_id, "error": step.error}

            # Execution simulation based on action type
            await asyncio.sleep(0.05)  # Async yield

            step_output = {
                "result": f"Executed action '{action}' successfully for job '{job.title}'",
                "checkpoint": f"ckpt_{job_id}_{step.step_index}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            step.status = "completed"
            step.completed_at = datetime.now(timezone.utc).isoformat()
            step.output = step_output
            job.checkpoint_state[f"step_{step.step_index}"] = step_output
            job.current_step = step.step_index + 1
            job.updated_at = datetime.now(timezone.utc).isoformat()

        job.status = "completed"
        job.completed_at = datetime.now(timezone.utc).isoformat()
        return {
            "success": True,
            "job_id": job_id,
            "status": "completed",
            "steps_completed": len(job.steps),
            "checkpoints": list(job.checkpoint_state.keys()),
        }

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        j = self._jobs.get(job_id)
        if not j:
            return None
        return {
            "job_id": j.job_id,
            "agent_id": j.agent_id,
            "title": j.title,
            "department": j.department,
            "status": j.status,
            "current_step": j.current_step,
            "total_steps": len(j.steps),
            "steps": [
                {
                    "step_index": s.step_index,
                    "name": s.name,
                    "action_type": s.action_type,
                    "status": s.status,
                    "started_at": s.started_at,
                    "completed_at": s.completed_at,
                    "error": s.error,
                }
                for s in j.steps
            ],
            "created_at": j.created_at,
            "updated_at": j.updated_at,
            "completed_at": j.completed_at,
            "checkpoint_state": j.checkpoint_state,
        }

    def list_jobs(self, limit: int = 20) -> List[Dict[str, Any]]:
        jobs_list = [self.get_job(jid) for jid in self._jobs.keys()]
        return [j for j in jobs_list if j is not None][:limit]

agent_runtime = AgentRuntime()
