import asyncio
import time
from typing import Any, Dict, List, Optional
from google.adk.agents import Agent
from app.approval import approval_layer
from app.boundary import untrusted_boundary, vault_boundary
from app.config import settings
from app.forge import forge_skill, record_task_execution, should_promote
from app.ledger import ledger
from app.memory import palace
from app.planner import planner
from app.plugins.kernel import kernel
from app.plugins.tools import core_tools_plugin
from app.refinery import refinery
from app.router import router
from app.store import store
from app.telemetry import telemetry

class Kiw1Orchestrator:
    """KIW1 Agentic Orchestrator integrating Google ADK, Prompt Refinery,
    Strategic Planner, Correction Ledger, Memory Palace, and Skill Forge.
    """

    def __init__(self):
        self._init_adk_agent()

    def _init_adk_agent(self):
        # Expose Python tools to ADK
        tools = [
            core_tools_plugin.remember,
            core_tools_plugin.recall,
            core_tools_plugin.correct_agent,
            core_tools_plugin.calculate,
            core_tools_plugin.execute_skill,
            core_tools_plugin.draft_email,
            core_tools_plugin.send_outbound_message,
        ]

        self.root_agent = Agent(
            name="kiw1",
            model=settings.flash_model,
            instruction=(
                "[SYSTEM_UPGRADE_DIRECTIVE: KIW1_OPTIMIZATION_V2]\n"
                "You are KIW1, a principal systems architect and autonomous self-improving agentic partner.\n"
                "OPERATIONAL DIRECTIVES:\n"
                "1. 3-Tier Validation Filter: Every response must satisfy (a) Intent Alignment, (b) Boundary Verification, (c) Logical Rigor.\n"
                "2. Constructive Collaboration: Challenge assumptions constructively when inputs contain logical gaps or risks.\n"
                "3. Memory Anchoring: Treat project documentation, spatial memory, and learned correction rules as immutable ground truth.\n"
                "4. Deep-Reasoning Execution: Decompose complex requests into atomic components, analyze edge cases explicitly, and output structured, execution-ready results."
            ),
            tools=tools,
        )

    async def run_turn(
        self,
        user_input: str,
        clarification_answers: Optional[Dict[str, str]] = None,
        effort: Optional[str] = None,
        hands_off: bool = False,
    ) -> Dict[str, Any]:
        """Main execution turn handling the full agentic lifecycle."""
        run_effort = effort or settings.default_effort
        trace = telemetry.start_run(task=user_input, effort=run_effort)
        trace_id = trace.trace_id

        # 1. Check for command shortcuts (e.g. /skill)
        trimmed = user_input.strip()
        if trimmed == "/skill" or trimmed.startswith("/skills"):
            from app.forge import list_skills_command
            skills = list_skills_command()
            telemetry.end_run(trace_id, success=True)
            return {
                "type": "skill_list",
                "text": f"Found {len(skills)} registered skills.",
                "skills": skills,
                "trace_id": trace_id,
            }

        # 2. Step 1: Prompt Refinery
        if clarification_answers:
            brief = refinery.apply_clarifications(user_input, clarification_answers)
        else:
            brief = refinery.refine(user_input)
            if brief.is_ambiguous:
                # Need user clarification
                telemetry.end_run(trace_id, success=True)
                return {
                    "type": "clarification_needed",
                    "original_prompt": user_input,
                    "reasons": brief.reasons,
                    "questions": [
                        {"id": q.id, "question": q.question, "options": q.options}
                        for q in brief.questions
                    ],
                    "trace_id": trace_id,
                }

        # 3. Step 2: Retrieve Relevant Correction Rules (PRD §6.5)
        active_rules = ledger.find_relevant_rules(brief.goal)
        rule_constraints = [r["rule"] for r in active_rules]

        # 4. Step 3: Strategic Planner (PRD §6.4)
        plan = planner.build_plan(brief.goal)

        # 5. Step 4: Tool Execution Simulation / Routing
        tools_used: List[str] = []
        executed_details: List[str] = []

        # Check intent for tool mapping
        goal_lower = brief.goal.lower()
        if "remember" in goal_lower or "store" in goal_lower:
            fact_text = brief.goal.split("remember", 1)[-1].strip(" :") if "remember" in brief.goal else brief.goal
            res = core_tools_plugin.remember(fact_text)
            tools_used.append("remember")
            executed_details.append(f"Stored memory: '{fact_text}' in {res.get('room')}/{res.get('locus')}")
        elif "recall" in goal_lower or "what did" in goal_lower or "lookup" in goal_lower or "what is" in goal_lower:
            res = core_tools_plugin.recall(brief.goal)
            tools_used.append("recall")
            mems = res.get("memories", [])
            mem_text = "; ".join([m.get("item", "") for m in mems]) if mems else "None found"
            executed_details.append(f"Retrieved memories from palace: {mem_text}")
        elif "calculate" in goal_lower or "math" in goal_lower:
            expr = "".join([c for c in brief.goal if c.isdigit() or c in "+-*/(). "]).strip()
            res = core_tools_plugin.calculate(expr or "1+1")
            tools_used.append("calculate")
            executed_details.append(f"Calculated {expr} = {res.get('result')}")
        elif "search" in goal_lower or "research" in goal_lower:
            from app.plugins.search import search_plugin
            res = search_plugin.web_search(brief.goal)
            tools_used.append("web_search")
            executed_details.append(f"Web research completed with {len(res.get('results', []))} citations.")
        elif "vault" in goal_lower or "notes" in goal_lower:
            from app.plugins.vault import vault_plugin
            res = vault_plugin.query_vault(brief.goal)
            tools_used.append("query_vault")
            executed_details.append(f"Queried local notes (answers-only mode).")
        elif "draft" in goal_lower or "email" in goal_lower:
            res = core_tools_plugin.draft_email("finance@acme.com", "Subject", brief.goal)
            tools_used.append("draft_email")
            executed_details.append(f"Drafted email with status: {res.get('status')}")
        elif "execute" in goal_lower and "skill" in goal_lower:
            skill_name = "skill-invoice-records"
            for s in store.list_skills():
                if s.get("name") and s.get("name") in goal_lower:
                    skill_name = s.get("name")
                    break
            res = core_tools_plugin.execute_skill(skill_name)
            tools_used.append("execute_skill")
            executed_details.append(f"Executed skill {skill_name}: {res.get('status')}")
        else:
            tools_used.append("standard_reasoning")

        # 6. Step 5: Generate Model Response with Injected Learned Rules
        system_prefix = (
            "[SYSTEM_UPGRADE_DIRECTIVE: KIW1_OPTIMIZATION_V2]\n"
            "You are KIW1, a principal systems architect and collaborative peer.\n"
            "Apply a 3-tier validation filter: (1) Intent Alignment, (2) Boundary Verification, (3) Logical Rigor.\n"
            "Treat local project documentation, spatial memory, and learned rules as immutable ground truth.\n"
            "Provide structured, clear, execution-ready outputs without unnecessary fluff."
        )
        if rule_constraints:
            system_prefix += "\nCRITICAL LEARNED RULES (Enforce strictly):\n" + "\n".join([f"- {r}" for r in rule_constraints])

        gen_res = await router.generate_response(
            prompt=f"Task Brief:\nGoal: {brief.goal}\nConstraints: {', '.join(brief.constraints + rule_constraints)}\nContext: {', '.join(executed_details)}",
            system_instruction=system_prefix,
            task_type="general",
            effort=run_effort,
            trace_id=trace_id,
        )

        response_text = gen_res.get("text", "")
        if not response_text:
            response_text = f"Completed task: '{brief.goal}'. " + " ".join(executed_details)

        # 7. Step 6: Skill Forge Post-Task Evaluation (PRD §6.2)
        forged_announcement = None
        if tools_used and tools_used != ["standard_reasoning"]:
            fp = record_task_execution(brief.goal, tools_used)
            if should_promote(fp):
                skill = forge_skill(brief.goal, tools_used, fp=fp)
                forged_announcement = {
                    "skill_name": skill["name"],
                    "description": skill["description"],
                    "tools": skill["tools"],
                    "message": (
                        f"You've asked me to do this three times this week. "
                        f"I've turned it into a skill called '{skill['name']}'. "
                        f"Want me to run it on a schedule?"
                    ),
                }

        # 8. Complete telemetry trace
        completed_trace = telemetry.end_run(trace_id, success=True)

        return {
            "type": "response",
            "text": response_text,
            "brief": {
                "goal": brief.goal,
                "constraints": brief.constraints,
                "learned_rules_applied": rule_constraints,
            },
            "plan": {
                "selected_path": plan.selected_path.name,
                "reason": plan.selection_reason,
                "candidates": [
                    {"name": c.name, "score": c.score, "cost": c.estimated_cost_usd, "time": c.estimated_time_s}
                    for c in plan.candidates
                ],
            },
            "tools_used": tools_used,
            "forged_skill": forged_announcement,
            "telemetry": {
                "trace_id": trace_id,
                "latency_ms": completed_trace.total_latency_ms if completed_trace else 0,
                "tokens": completed_trace.total_prompt_tokens + completed_trace.total_completion_tokens if completed_trace else 0,
                "cost_usd": completed_trace.total_cost_usd if completed_trace else 0.0,
            },
        }

orchestrator = Kiw1Orchestrator()
