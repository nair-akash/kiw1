import argparse
import asyncio
import json
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Tuple
from app.agent import orchestrator
from app.config import settings
from app.forge import forge_skill
from app.ledger import ledger
from app.memory import palace
from app.router import router
from app.store import store

TASKS_FILE = Path(__file__).parent / "benchmark_tasks.json"
RESULTS_FILE = Path(__file__).parent / "results.json"
STATIC_RESULTS_FILE = Path(__file__).parent.parent / "app" / "static" / "results.json"

class BenchmarkRunner:
    def __init__(self):
        with open(TASKS_FILE, "r") as f:
            self.tasks = json.load(f)

    async def run_single_task(self, task: Dict[str, Any]) -> Tuple[bool, str]:
        """Evaluates a single task deterministically through the real agent orchestrator.
        The exact same code path and assertion are used for both cold and learned runs.
        """
        task_id = task["id"]
        prompt = task["prompt"]
        assertion_type = task.get("assertion_type", "")
        assertion_value = task.get("assertion_value", "")

        try:
            # 1. Execute through the standard agent orchestrator entry point
            turn_res = await orchestrator.run_turn(prompt)

            # 2. Evaluate assertion based on the declared assertion specification
            if assertion_type == "output_contains":
                text = turn_res.get("text", "")
                passed = assertion_value.lower() in text.lower()
                detail = f"Found '{assertion_value}' in output" if passed else f"Expected '{assertion_value}' in output"
                return passed, detail

            elif assertion_type == "response_type":
                res_type = turn_res.get("type", "")
                passed = res_type == assertion_value
                detail = f"Response type: '{res_type}' (expected '{assertion_value}')"
                return passed, detail

            elif assertion_type == "tool_used":
                tools = turn_res.get("tools_used", [])
                passed = assertion_value in tools
                detail = f"Tools used: {tools} (expected '{assertion_value}')"
                return passed, detail

            elif assertion_type == "learned_rule_applied":
                rules = turn_res.get("brief", {}).get("learned_rules_applied", [])
                passed = any(assertion_value.lower() in r.lower() for r in rules)
                detail = f"Injected rules: {rules} (expected '{assertion_value}')"
                return passed, detail

            elif assertion_type == "has_learned_rules":
                rules = turn_res.get("brief", {}).get("learned_rules_applied", [])
                passed = len(rules) > 0
                detail = f"Found {len(rules)} active injected rules" if passed else "No relevant rules injected"
                return passed, detail

            elif assertion_type == "plan_candidates_count":
                candidates = turn_res.get("plan", {}).get("candidates", [])
                count = len(candidates)
                passed = count == assertion_value
                detail = f"Scored {count} candidate paths (expected {assertion_value})"
                return passed, detail

            else:
                return False, f"Unknown assertion type: {assertion_type}"

        except Exception as e:
            return False, f"Execution error: {str(e)}"

    async def run_benchmark(self) -> Dict[str, Any]:
        """Runs the 20-task benchmark: Cold Run -> Learning Session -> Learned Run."""
        print("=================================================================", flush=True)
        print("          KIW1 20-TASK SELF-IMPROVEMENT BENCHMARK                ", flush=True)
        print("=================================================================", flush=True)

        deterministic_count = sum(1 for t in self.tasks if t.get("deterministic", True))
        judged_count = len(self.tasks) - deterministic_count
        print(f"Task suite: {len(self.tasks)} tasks ({deterministic_count} deterministic, {judged_count} judged)", flush=True)

        # 1. Cold Run (empty state)
        print("\n--- PHASE 1: COLD RUN (Empty memory, no corrections, no forged skills) ---", flush=True)
        store.reset_for_benchmark()
        cold_results = []
        cold_passed = 0

        for task in self.tasks:
            passed, detail = await self.run_single_task(task)
            if passed:
                cold_passed += 1
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {task['id']} - {task['name']}: {detail}", flush=True)
            cold_results.append({
                "id": task["id"],
                "name": task["name"],
                "passed": passed,
                "detail": detail,
            })

        print(f"\n>>> COLD RUN SCORE: {cold_passed} / {len(self.tasks)} ({int(cold_passed / len(self.tasks) * 100)}%)", flush=True)

        # 2. Learning Session
        print("\n--- PHASE 2: LEARNING SESSION (Recording corrections, forging skills, updating palace) ---", flush=True)
        # Corrections
        ledger.record_correction(
            situation="formatting invoices",
            wrong_action="using plain text table",
            correction="always format as structured markdown with GST breakdown",
        )
        ledger.record_correction(
            situation="displaying timestamps or dates",
            wrong_action="using US MM/DD/YYYY format",
            correction="use ISO YYYY-MM-DD format",
        )
        # Memory storage
        palace.store_memory("Our confidential project codename is Project Falcon.", room="projects", locus="falcon")
        palace.store_memory("My preferred timezone is Pacific/Auckland.", room="preferences", locus="timezone")
        palace.store_memory("The primary client contact email is client@acme.corp.", room="projects", locus="acme")
        palace.store_memory("The team lead for KIW1 is Sarah Chen.", room="knowledge", locus="team")

        # Forged skills
        forge_skill("format invoice records", ["calculate", "remember"], name="skill-invoice-records")
        forge_skill("invoice audit", ["calculate", "draft_email"], name="skill-invoice-audit")
        print("Learned rules recorded, spatial memories stored, and skills registered in store.", flush=True)

        # 3. Learned Run (same tasks, same prompts, same assertions)
        print("\n--- PHASE 3: LEARNED RUN (Identical 20 tasks after learning) ---", flush=True)
        learned_results = []
        learned_passed = 0

        for task in self.tasks:
            passed, detail = await self.run_single_task(task)
            if passed:
                learned_passed += 1
            status = "PASS" if passed else "FAIL"
            print(f"[{status}] {task['id']} - {task['name']}: {detail}", flush=True)
            learned_results.append({
                "id": task["id"],
                "name": task["name"],
                "passed": passed,
                "detail": detail,
            })

        print(f"\n>>> LEARNED RUN SCORE: {learned_passed} / {len(self.tasks)} ({int(learned_passed / len(self.tasks) * 100)}%)", flush=True)
        delta = learned_passed - cold_passed
        delta_pct = int((delta / len(self.tasks)) * 100)
        print(f">>> IMPROVEMENT DELTA: +{delta} tasks (+{delta_pct}%)", flush=True)
        print("=================================================================\n", flush=True)

        summary = {
            "total_tasks": len(self.tasks),
            "deterministic_tasks": deterministic_count,
            "judged_tasks": judged_count,
            "cold_score": f"{cold_passed}/{len(self.tasks)}",
            "cold_percentage": f"{int(cold_passed / len(self.tasks) * 100)}%",
            "learned_score": f"{learned_passed}/{len(self.tasks)}",
            "learned_percentage": f"{int(learned_passed / len(self.tasks) * 100)}%",
            "delta": f"+{delta}",
            "delta_percentage": f"+{delta_pct}%",
            "cold_results": cold_results,
            "learned_results": learned_results,
        }

        with open(RESULTS_FILE, "w") as f:
            json.dump(summary, f, indent=2)

        try:
            with open(STATIC_RESULTS_FILE, "w") as f:
                json.dump(summary, f, indent=2)
        except Exception:
            pass

        return summary

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KIW1 20-Task Benchmark Runner")
    args = parser.parse_args()

    runner = BenchmarkRunner()
    asyncio.run(runner.run_benchmark())
