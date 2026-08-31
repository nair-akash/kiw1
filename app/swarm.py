import asyncio
import time
from typing import Any, Dict, List, Optional
from app.ledger import ledger
from app.memory import palace
from app.plugins.search import search_plugin
from app.router import router

class SwarmAgent:
    """Specialized Sub-Agent Persona within the KIW1 Multi-Agent Swarm."""

    def __init__(self, name: str, role: str, icon: str, system_prompt: str):
        self.name = name
        self.role = role
        self.icon = icon
        self.system_prompt = system_prompt

    async def execute(self, task: str, shared_context: Dict[str, Any], trace_id: Optional[str] = None) -> Dict[str, Any]:
        prompt = (
            f"Role: {self.role}\n"
            f"User Goal: {task}\n"
            f"Shared Context: {shared_context}\n\n"
            f"Provide your specialized domain assessment and findings concisely."
        )
        res = await router.generate_response(
            prompt=prompt,
            system_instruction=self.system_prompt,
            task_type="swarm_agent",
            effort="quick",
            trace_id=trace_id,
        )
        return {
            "agent": self.name,
            "role": self.role,
            "icon": self.icon,
            "assessment": res.get("text", ""),
            "tokens": res.get("total_tokens", 0) or res.get("prompt_tokens", 0),
            "status": "completed",
        }


class SwarmOrchestrator:
    """Orchestrates parallel execution and consensus among specialized sub-agents."""

    def __init__(self):
        self.agents = [
            SwarmAgent(
                name="Architect",
                role="Systems & Logic Architect",
                icon="🛠️",
                system_prompt="You are the Systems Architect. Focus on structural integrity, computational efficiency, and deterministic patterns.",
            ),
            SwarmAgent(
                name="Security Auditor",
                role="Data Boundary & Risk Sentinel",
                icon="🛡️",
                system_prompt="You are the Security Auditor. Focus on untrusted input sanitization, risk classification, and safety constraints.",
            ),
            SwarmAgent(
                name="Research Analyst",
                role="Fact & Empirical Grounding",
                icon="🔬",
                system_prompt="You are the Research Analyst. Focus on factual verification, citation tracking, and empirical rigor.",
            ),
            SwarmAgent(
                name="Memory Custodian",
                role="Spatial Palace & Rules Custodian",
                icon="🧠",
                system_prompt="You are the Memory Custodian. Ensure alignment with user preferences, correction ledger rules, and historical facts.",
            ),
        ]

    async def orchestrate_swarm(self, task: str, trace_id: Optional[str] = None) -> Dict[str, Any]:
        """Runs parallel sub-agent evaluations and synthesizes collective consensus."""
        start_time = time.perf_counter()

        # Step 1: Collect shared baseline context
        relevant_rules = ledger.find_relevant_rules(task)
        memory_hits = palace.retrieve(task, limit=3)
        shared_context = {
            "active_rules": [r.get("rule") for r in relevant_rules],
            "spatial_memories": [m.get("item") for m in memory_hits],
        }

        # Step 2: Parallel execution across all sub-agents
        agent_tasks = [
            agent.execute(task, shared_context, trace_id=trace_id)
            for agent in self.agents
        ]
        agent_results = await asyncio.gather(*agent_tasks)

        # Step 3: Synthesis Pass (Gemini 3.7 Flash)
        synthesis_prompt = f"""Synthesize the multi-agent swarm findings into a unified, high-confidence plan.

User Task: {task}

Sub-Agent Findings:
"""
        for r in agent_results:
            synthesis_prompt += f"\n[{r['icon']} {r['agent']} - {r['role']}]:\n{r['assessment']}\n"

        synthesis_prompt += "\nProduce a coherent, execution-ready summary combining all perspectives."

        synth_res = await router.generate_response(
            prompt=synthesis_prompt,
            system_instruction="You are KIW1 Swarm Master. Synthesize multi-agent outputs cleanly and authoritatively.",
            task_type="swarm_synthesis",
            effort="standard",
            trace_id=trace_id,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "task": task,
            "swarm_results": agent_results,
            "consensus": synth_res.get("text", ""),
            "agent_count": len(self.agents),
            "elapsed_ms": round(elapsed_ms, 2),
        }

swarm_orchestrator = SwarmOrchestrator()
