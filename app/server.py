import os
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
async def get_research_reports():
    return {
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
