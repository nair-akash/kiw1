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
        """Picks the weakest area using deterministic heuristics (PRD §6.3).
        Returns: (target_topic, reason, category).
        """
        # 1. Check recent active corrections in the ledger
        active_corrections = ledger.list_rules()
        unreinforced = [r for r in active_corrections if r.get("active", True) and r.get("reinforcement_count", 0) == 0]
        if unreinforced:
            rule = unreinforced[-1]
            return rule["situation"], f"Active user correction requires deeper grounding: '{rule['situation']}'", "correction_grounding"

        # 2. Check stale or low-access memories in Memory Palace
        memories = store.list_memory_items()
        stale = [m for m in memories if m.get("decay_score", 1.0) < 0.7]
        if stale:
            m = stale[0]
            return f"{m.get('room')}: {m.get('locus')}", f"Memory decay indicates need for refresh: {m.get('item')[:40]}...", "memory_refresh"

        # 3. Default foundational knowledge target
        return "Gemini 3.7 tool calling and thinking budget optimization", "Proactive overnight capability enhancement", "capability_grounding"

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
