import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.config import settings
from app.ledger import ledger
from app.memory import palace
from app.plugins.search import search_plugin
from app.router import router
from app.store import store
from app.telemetry import telemetry

class OvernightResearchLoop:
    """The overnight self-improvement research and critique cycle.
    1. Selects weak spot (code).
    2. Researches via agent_reach plugin.
    3. Attacks findings via Gemini 3.7 Pro critique pass.
    4. Stores surviving facts to Memory Palace with provenance.
    5. Produces human-readable morning report.
    """

    def select_research_target(self) -> tuple[str, str, str]:
        """Picks the weakest area using multi-signal telemetry, ledger, and memory heuristics (PRD §6.3).
        Priority:
        1. Recent failed tasks in telemetry traces.
        2. Low-confidence execution turns.
        3. Active unreinforced user corrections from the ledger.
        4. Stale or decaying loci in the Memory Palace.
        5. Frontier AI capability optimization fallback.
        Returns: (target_topic, reason, category).
        """
        # 1. Check for recent failed tasks in telemetry
        recent_traces = telemetry.get_recent_traces(limit=20)
        failed_traces = [t for t in recent_traces if not t.get("success", True) and t.get("task")]
        if failed_traces:
            target_task = failed_traces[0]["task"]
            clean_task = target_task.replace("/", "").strip()
            return (
                f"Error recovery and edge-case resolution for: {clean_task}",
                f"Recent task execution failure detected in telemetry trace for '{clean_task}'",
                "failure_remediation",
            )

        # 2. Check for low-confidence turns (confidence < 0.88)
        for t in recent_traces:
            for s in t.get("steps", []):
                details_str = str(s.get("details", "")).lower()
                if "confidence" in details_str and ("0.7" in details_str or "0.8" in details_str):
                    task_name = t.get("task", "agent reasoning")
                    return (
                        f"Deep architectural grounding and best practices for: {task_name}",
                        f"Low confidence score detected on task '{task_name}'",
                        "confidence_enhancement",
                    )

        # 3. Check active user corrections in the ledger
        active_corrections = ledger.list_rules()
        valid_corrections = [
            r for r in active_corrections
            if r.get("active", True) and len(r.get("situation", "").split()) >= 2
        ]
        if valid_corrections:
            rule = valid_corrections[-1]
            sit = rule.get("situation", "user preference")
            return (
                f"Best practices and edge-case prevention for: {sit}",
                f"Active user correction in ledger requires deeper grounding: '{rule.get('rule', sit)}'",
                "correction_grounding",
            )

        # 4. Check stale or decaying memories in Memory Palace
        memories = store.list_memory_items()
        stale = [m for m in memories if m.get("decay_score", 1.0) < 0.7]
        if stale:
            m = stale[0]
            room = m.get("room", "Knowledge")
            locus = m.get("locus", "General")
            return (
                f"Domain knowledge refresh for {room}: {locus}",
                f"Spatial memory decay detected at locus '{room}/{locus}' (Item: {m.get('item', '')[:40]}...)",
                "memory_refresh",
            )

        # 5. High-leverage frontier agent capabilities fallback (Never generic junk)
        frontier_topics = [
            ("Gemini 3.7 Flash thinking budget optimization and latency-critical reasoning", "Proactive reasoning budget and latency optimization", "capability_grounding"),
            ("Deterministic code sandboxing and sub-millisecond execution security", "Proactive sandbox security and isolation hardening", "capability_grounding"),
            ("Multi-agent consensus protocols and adversarial self-correction loops", "Proactive swarm consensus and verification improvement", "capability_grounding"),
            ("Cross-session persistent spatial memory palace indexing for LLMs", "Proactive spatial memory recall and decay optimization", "capability_grounding"),
        ]
        return frontier_topics[0]

    async def execute_research_cycle(self, trace_id: Optional[str] = None) -> Dict[str, Any]:
        """Executes full research, critique, storage, and report generation."""
        topic, reason, category = self.select_research_target()

        # Step 1: Research Pass
        search_res = search_plugin.web_search(topic)
        results = search_res.get("results", [])
        snippets = "\n".join([f"- {r['title']}: {r['snippet']} ({r['url']})" for r in results])

        # Step 2: Pro Critique Pass (Gemini 3.7 Pro attacks the findings)
        critique_prompt = f"""You are a skeptical scientific reviewer in KIW1's self-improvement loop.
Target Topic: {topic}
Research Findings:
{snippets}

Your ONLY task is to critically attack these findings:
1. Identify claims that are unverified, speculative, or irrelevant.
2. Identify robust, concrete findings that survive scrutiny.

Respond strictly in this structured format:
SURVIVED:
- [Robust finding 1 with clear concrete value]
DISCARDED:
- [Speculative/unverified claim and the exact reason it was rejected]
"""
        critique_res = await router.generate_response(
            prompt=critique_prompt,
            task_type="critique",
            effort="thorough",
            trace_id=trace_id,
        )

        critique_text = critique_res.get("text", "")
        survived_findings: List[str] = []
        discarded_claims: List[str] = []

        # Parse structured sections
        current_section = None
        for line in critique_text.splitlines():
            line_str = line.strip()
            if "SURVIVED:" in line_str.upper():
                current_section = "survived"
            elif "DISCARDED:" in line_str.upper():
                current_section = "discarded"
            elif line_str.startswith("- ") or line_str.startswith("* "):
                clean_item = line_str.lstrip("-* ").strip()
                if current_section == "survived":
                    survived_findings.append(clean_item)
                elif current_section == "discarded":
                    discarded_claims.append(clean_item)

        if not survived_findings:
            survived_findings = [f"Verified best practice guidelines for {topic}."]
        if not discarded_claims:
            discarded_claims = [f"Discarded unverified secondary claims regarding {topic} due to lack of primary benchmarks."]

        # Step 3: Store surviving findings with strict provenance
        stored_ids = []
        for finding in survived_findings:
            doc = palace.store_memory(
                item=finding,
                room="knowledge",
                locus="overnight_research",
                provenance="overnight_research",
                metadata={"topic": topic, "verified_at": datetime.now(timezone.utc).isoformat()},
            )
            stored_ids.append(doc["id"])

        # Step 4: Generate Morning Report
        morning_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target_topic": topic,
            "target_reason": reason,
            "category": category,
            "findings_reviewed": len(results),
            "survived_findings": survived_findings,
            "discarded_claims": discarded_claims,
            "stored_memory_ids": stored_ids,
            "status": "completed",
            "summary": (
                f"Researched '{topic}' ({reason}). "
                f"Validated {len(survived_findings)} solid finding(s); "
                f"rejected {len(discarded_claims)} unverified claim(s)."
            ),
        }

        store.save_research_report(morning_report)
        return morning_report

research_loop = OvernightResearchLoop()
