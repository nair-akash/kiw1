import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.agent import orchestrator
from app.config import settings
from app.forge import forge_skill, list_skills_command, record_skill_outcome
from app.ledger import ledger
from app.memory import palace
from app.plugins.kernel import kernel
from app.plugins.tools import core_tools_plugin
from app.research import research_loop
from app.store import store
from app.telemetry import telemetry

app = FastAPI(
    title="KIW1 Agentic Harness",
    description="Autonomous self-improving agent that writes its own skills and researches overnight.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Models
class ChatRequest(BaseModel):
    message: str
    effort: Optional[str] = "standard"
    hands_off: Optional[bool] = False
    clarification_answers: Optional[Dict[str, str]] = None
    attachments: Optional[List[Dict[str, Any]]] = None

class ClarifyRequest(BaseModel):
    original_prompt: str
    answers: Dict[str, str]
    effort: Optional[str] = "standard"

class CorrectionRequest(BaseModel):
    situation: str
    wrong_action: str
    correction: str

class MemoryRequest(BaseModel):
    fact: str
    room: Optional[str] = None
    locus: Optional[str] = None

class SkillExecutionRequest(BaseModel):
    skill_name: str
    parameters: Optional[Dict[str, Any]] = None

# API Endpoints
@app.get("/healthz")
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "kiw1-agent",
        "model_default": settings.flash_model,
        "cloud_mode": store.is_cloud(),
        "vault_mode": settings.vault_mode,
    }

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        result = await orchestrator.run_turn(
            user_input=req.message,
            clarification_answers=req.clarification_answers,
            effort=req.effort,
            hands_off=req.hands_off or False,
            attachments=req.attachments,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clarify")
async def clarify_endpoint(req: ClarifyRequest):
    try:
        result = await orchestrator.run_turn(
            user_input=req.original_prompt,
            clarification_answers=req.answers,
            effort=req.effort,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/skills")
async def get_skills():
    return {
        "skills": list_skills_command(),
        "total": len(store.list_skills()),
    }

@app.post("/api/skills/execute")
async def execute_skill_endpoint(req: SkillExecutionRequest):
    res = core_tools_plugin.execute_skill(req.skill_name, req.parameters)
    return res

@app.post("/api/skills/feedback")
async def skill_feedback(skill_name: str, outcome: str):
    updated = record_skill_outcome(skill_name, outcome)
    if not updated:
        raise HTTPException(status_code=404, detail="Skill not found")
    return updated

@app.get("/api/corrections")
async def get_corrections():
    return {
        "rules": ledger.list_rules(),
        "active_count": len([r for r in ledger.list_rules() if r.get("active", True)]),
    }

@app.post("/api/corrections")
async def add_correction_endpoint(req: CorrectionRequest):
    res = ledger.record_correction(req.situation, req.wrong_action, req.correction)
    return res

@app.get("/api/memory")
async def get_memory():
    return {
        "tree": palace.get_palace_tree(),
        "recent_items": palace.retrieve("", limit=20),
    }

@app.post("/api/memory")
async def add_memory_endpoint(req: MemoryRequest):
    res = palace.store_memory(req.fact, room=req.room, locus=req.locus)
    return res

@app.get("/api/telemetry")
async def get_telemetry():
    return {
        "traces": telemetry.get_recent_traces(limit=20),
    }

@app.post("/research/run")
@app.post("/api/research/trigger")
async def trigger_overnight_research():
    """Cloud Scheduler webhook endpoint to run overnight research loop."""
    try:
        report = await research_loop.execute_research_cycle()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/research/reports")
@app.get("/api/research/brief")
async def get_research_reports():
    return {
        "status": "ready",
        "reports": store.list_research_reports(),
    }

@app.get("/api/plugins")
async def get_plugins():
    return {
        "plugins": kernel.list_plugins(),
    }

@app.get("/api/evals")
async def get_eval_results():
    results_path = Path(__file__).parent / "static" / "results.json"
    if results_path.exists():
        import json
        with open(results_path, "r") as f:
            return json.load(f)
    return {"status": "no_results_yet"}

@app.post("/api/evals/run")
async def run_evals_endpoint():
    try:
        from evals.runner import BenchmarkRunner
        runner = BenchmarkRunner()
        summary = await runner.run_benchmark()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class SandboxRequest(BaseModel):
    code: str

class SwarmRequest(BaseModel):
    task: str

@app.post("/api/sandbox/run")
async def run_sandbox_code(req: SandboxRequest):
    from app.plugins.sandbox import sandbox_plugin
    res = sandbox_plugin.execute_python_code(req.code)
    return res

@app.post("/api/swarm/execute")
async def execute_swarm_task(req: SwarmRequest):
    from app.swarm import swarm_orchestrator
    res = await swarm_orchestrator.orchestrate_swarm(req.task)
    return res

# Autonomous Commitments & Delivery Ledger Endpoints
class CreateCommitmentRequest(BaseModel):
    skill_name: str
    cadence: Optional[str] = None
    cron_expression: Optional[str] = None
    provenance: Optional[str] = "agent_self_derived"

@app.get("/api/commitments")
async def get_commitments():
    return {
        "commitments": store.list_commitments(),
        "total": len(store.list_commitments()),
    }

@app.post("/api/commitments/create")
async def create_commitment_endpoint(req: CreateCommitmentRequest):
    from app.commitments import commitment_manager
    cmt = commitment_manager.create_commitment(
        skill_name_or_id=req.skill_name,
        cadence=req.cadence,
        cron_expr=req.cron_expression,
        provenance=req.provenance or "agent_self_derived",
    )
    return {"success": True, "commitment": cmt}

@app.post("/api/commitments/{cid}/trigger")
async def trigger_commitment_endpoint(cid: str):
    from app.commitments import commitment_manager
    res = await commitment_manager.execute_commitment(cid, force=True)
    return res

@app.post("/api/commitments/{cid}/pause")
async def pause_commitment_endpoint(cid: str):
    store.update_commitment(cid, {"status": "paused", "enabled": False})
    return {"success": True, "status": "paused"}

@app.post("/api/commitments/{cid}/resume")
async def resume_commitment_endpoint(cid: str):
    store.update_commitment(cid, {"status": "active", "enabled": True})
    return {"success": True, "status": "active"}

@app.delete("/api/commitments/{cid}")
async def delete_commitment_endpoint(cid: str):
    deleted = store.delete_commitment(cid)
    return {"success": deleted}

@app.get("/api/deliveries")
async def get_deliveries():
    return {
        "deliveries": store.list_deliveries(),
        "total": len(store.list_deliveries()),
    }

@app.get("/api/session/proactive")
async def get_proactive_announcement():
    from app.commitments import commitment_manager
    announcement = commitment_manager.get_proactive_announcement()
    return {"announcement": announcement}

@app.get("/api/evals/frontier")
async def get_frontier_evals():
    frontier_file = Path(__file__).parent.parent / "evals" / "frontier_results.json"
    if frontier_file.exists():
        with open(frontier_file, "r") as f:
            return json.load(f)
    from evals.frontier_benchmarks import frontier_runner
    return await frontier_runner.run_full_suite()

# Enterprise Agent Registry Endpoints
class PublishAgentRequest(BaseModel):
    name: str
    department: str
    description: str
    capabilities: List[str]
    allowed_tools: List[str]
    author: Optional[str] = "Enterprise Developer"
    version: Optional[str] = "1.0.0"
    metadata: Optional[Dict[str, Any]] = None

@app.get("/api/registry/agents")
async def get_registry_agents(department: Optional[str] = None, status: Optional[str] = None):
    from app.registry import agent_registry
    return {
        "agents": agent_registry.list_agents(department=department, status=status),
        "total": len(agent_registry.list_agents()),
    }

@app.get("/api/registry/agents/{aid}")
async def get_registry_agent(aid: str):
    from app.registry import agent_registry
    agent = agent_registry.get_agent(aid)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{aid}' not found")
    return agent

@app.post("/api/registry/publish")
async def publish_agent_endpoint(req: PublishAgentRequest):
    from app.registry import agent_registry
    agent = agent_registry.publish_agent(
        name=req.name,
        department=req.department,
        description=req.description,
        capabilities=req.capabilities,
        allowed_tools=req.allowed_tools,
        author=req.author or "Enterprise Developer",
        version=req.version or "1.0.0",
        metadata=req.metadata,
    )
    return {"success": True, "agent": agent}

# Model Armor Security Endpoints
class ArmorInspectRequest(BaseModel):
    text: str

@app.get("/api/armor/posture")
async def get_armor_posture():
    from app.armor import model_armor
    return model_armor.get_security_posture()

@app.post("/api/armor/inspect")
async def inspect_with_armor(req: ArmorInspectRequest):
    from app.armor import model_armor
    is_safe, sanitized, threats = model_armor.inspect_input(req.text)
    redacted, pii_count = model_armor.redact_pii_and_secrets(sanitized)
    return {
        "is_safe": is_safe,
        "threats": threats,
        "pii_redactions_applied": pii_count,
        "sanitized_output": redacted,
    }

# Zero-Trust Gateway Endpoints
@app.get("/api/gateway/audit")
async def get_gateway_audit(limit: int = 50):
    from app.gateway import agent_gateway
    return {
        "audit_trail": agent_gateway.get_audit_trail(limit=limit),
        "total": len(agent_gateway.get_audit_trail(limit=1000)),
    }

# Agent Runtime Endpoints
class CreateRuntimeJobRequest(BaseModel):
    agent_id: str
    title: str
    department: str
    steps: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None

@app.get("/api/runtime/jobs")
async def get_runtime_jobs(limit: int = 20):
    from app.runtime import agent_runtime
    return {
        "jobs": agent_runtime.list_jobs(limit=limit),
        "total": len(agent_runtime.list_jobs()),
    }

@app.post("/api/runtime/jobs/create")
async def create_runtime_job(req: CreateRuntimeJobRequest):
    from app.runtime import agent_runtime
    job = agent_runtime.create_job(
        agent_id=req.agent_id,
        title=req.title,
        department=req.department,
        steps=req.steps,
        metadata=req.metadata,
    )
    return {"success": True, "job": agent_runtime.get_job(job.job_id)}

@app.post("/api/runtime/jobs/{jid}/run")
async def run_runtime_job(jid: str):
    from app.runtime import agent_runtime
    res = await agent_runtime.execute_job(jid)
    return res

# OpenTelemetry Endpoints
@app.get("/api/telemetry/otel-traces")
async def get_otel_traces(limit: int = 15):
    from app.otel import otel_service
    return {
        "traces": otel_service.list_recent_traces(limit=limit),
        "total": len(otel_service.list_recent_traces(limit=100)),
    }

@app.get("/api/telemetry/otel-traces/{tid}")
async def get_otel_trace(tid: str):
    from app.otel import otel_service
    waterfall = otel_service.export_trace_waterfall(tid)
    if not waterfall.get("spans"):
        raise HTTPException(status_code=404, detail="Trace not found")
    return waterfall

# Taskmaster Heavy-Lifting Chore Automation
class TaskmasterChoreRequest(BaseModel):
    vendor_name: Optional[str] = "Acme Cloud Infrastructure Ltd"
    contract_value_usd: Optional[float] = 125000.0
    currency_base: Optional[str] = "USD"
    currency_target: Optional[str] = "INR"

@app.post("/api/taskmaster/run-chore")
async def run_taskmaster_chore(req: TaskmasterChoreRequest):
    from app.taskmaster import taskmaster
    res = await taskmaster.execute_vendor_compliance_chore(
        vendor_name=req.vendor_name or "Acme Cloud Infrastructure Ltd",
        contract_value_usd=req.contract_value_usd or 125000.0,
        currency_base=req.currency_base or "USD",
        currency_target=req.currency_target or "INR",
    )
    return res

# Mount static frontend
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/")
    async def serve_index():
        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        return {"message": "KIW1 Agent Core Running"}
