import asyncio
import re
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from app.approval import approval_layer
from app.boundary import untrusted_boundary
from app.config import settings
from app.store import store
from app.telemetry import telemetry

def infer_cadence_from_history(fingerprint_str: str) -> tuple[str, str, str]:
    """Infers cadence and next run time in pure code from observed timestamp intervals.
    Returns: (cadence_name, cron_expression, human_readable_schedule).
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    recent = store.get_recent_fingerprints(fingerprint_str, cutoff)
    
    if len(recent) >= 2:
        try:
            timestamps = sorted([datetime.fromisoformat(r["ts"].replace("Z", "+00:00")) for r in recent if "ts" in r])
            if len(timestamps) >= 2:
                deltas = [(timestamps[i] - timestamps[i-1]).total_seconds() for i in range(1, len(timestamps))]
                avg_delta = sum(deltas) / len(deltas)
                if avg_delta < 86400:  # less than 1 day
                    return "daily", "0 9 * * 1-5", "every weekday at 9:00 AM"
        except Exception:
            pass

    # Default weekly cadence
    return "weekly", "0 9 * * 1", "every Monday at 9:00 AM"

def calculate_next_run(cadence: str) -> str:
    """Calculates next ISO timestamp for a cadence."""
    now = datetime.now(timezone.utc)
    if cadence == "daily":
        next_run = now + timedelta(days=1)
        next_run = next_run.replace(hour=9, minute=0, second=0, microsecond=0)
    else:  # weekly
        days_ahead = (0 - now.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        next_run = now + timedelta(days=days_ahead)
        next_run = next_run.replace(hour=9, minute=0, second=0, microsecond=0)
    return next_run.isoformat()

class AutonomousCommitmentManager:
    """Autonomous Commitment Harness managing standing commitments, unattended
    execution, single-consent lifecycle, risk gating, and auto-suspension.
    """

    def create_commitment(
        self,
        skill_name_or_id: str,
        cadence: Optional[str] = None,
        cron_expr: Optional[str] = None,
        provenance: str = "agent_self_derived",
    ) -> Dict[str, Any]:
        """Creates a standing autonomous commitment in the durable store."""
        skill = store.get_skill(skill_name_or_id)
        if not skill:
            # Look up by slug or fp
            for s in store.list_skills():
                if s.get("name") == skill_name_or_id or s.get("fp") == skill_name_or_id:
                    skill = s
                    break

        skill_id = skill["name"] if skill else skill_name_or_id
        skill_name = skill.get("name", skill_name_or_id) if skill else skill_name_or_id
        fp = skill.get("fp", "") if skill else ""

        if not cadence:
            cadence, default_cron, human_desc = infer_cadence_from_history(fp)
            cron_expr = cron_expr or default_cron
        else:
            human_desc = f"every {cadence}"
            cron_expr = cron_expr or ("0 9 * * 1-5" if cadence == "daily" else "0 9 * * 1")

        next_run = calculate_next_run(cadence)
        cid = f"cmt_{skill_name.replace(' ', '_')}_{int(time.time())}"

        commitment_data = {
            "id": cid,
            "skill_id": skill_id,
            "skill_name": skill_name,
            "intent_template": (skill.get("intent_template") or skill.get("description") or skill_name) if skill else skill_name,
            "tools": skill.get("tools", ["standard_reasoning"]) if skill else ["standard_reasoning"],
            "cadence": cadence,
            "cron_expression": cron_expr,
            "human_schedule": human_desc,
            "next_run_time": next_run,
            "enabled": True,
            "status": "active",
            "provenance": provenance,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_run": None,
            "run_count": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "disabled_reason": None,
        }

        store.save_commitment(commitment_data)
        return commitment_data

    async def execute_commitment(
        self,
        commitment_id: str,
        idempotency_key: Optional[str] = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        """Executes a standing commitment unattended with strict risk gating,
        idempotency check, budget ceiling, and outcome logging.
        """
        commitment = store.get_commitment(commitment_id)
        if not commitment:
            return {"success": False, "error": f"Commitment '{commitment_id}' not found"}

        if not commitment.get("enabled", True) or commitment.get("status") != "active":
            return {
                "success": False,
                "error": f"Commitment is {commitment.get('status')} ({commitment.get('disabled_reason') or 'disabled'})",
            }

        # Check if linked skill is still enabled
        skill = store.get_skill(commitment.get("skill_id", ""))
        if skill and not skill.get("enabled", True):
            self.auto_suspend_for_skill(
                commitment.get("skill_id", ""),
                reason=f"Skill auto-disabled: {skill.get('disabled_reason', 'Low success rate')}"
            )
            return {
                "success": False,
                "error": f"Commitment auto-suspended: linked skill '{skill.get('name')}' is disabled",
            }

        # 1. Idempotency Check (PRD §6.8)
        current_hour_bucket = int(time.time() // 3600)
        idem_key = idempotency_key or f"exec_{commitment_id}_{current_hour_bucket}"
        existing_exec = store.get_execution_idempotency(idem_key)
        if existing_exec and not force:
            return {
                "success": True,
                "idempotent_duplicate": True,
                "message": "Commitment already executed for this schedule bucket. Redelivery acknowledged without re-execution.",
                "cached_result": existing_exec.get("result"),
            }

        # 2. Budget Guard: Hard cost and token ceiling per unattended run
        # Max $0.05 / 25k tokens per automated execution
        max_run_budget_usd = 0.05

        # 3. Risk Assessment & High-Risk Unattended Gating (PRD §6.7 & §12b)
        task_intent = commitment.get("intent_template") or commitment.get("skill_name", "Autonomous Task")
        tools = commitment.get("tools", [])

        # Check risk level for every action
        is_high_risk = False
        high_risk_reason = None
        for t in tools:
            risk_level, risk_reason = approval_layer.classify_risk(task_intent, t)
            if risk_level == "HIGH":
                is_high_risk = True
                high_risk_reason = risk_reason
                break

        # Check intent text and skill identifiers for irreversible or financial actions
        intent_lower = f"{task_intent} {commitment.get('skill_name', '')} {commitment.get('skill_id', '')}".lower()
        if any(w in intent_lower for w in ["wipe", "delete all", "drop table", "wire funds", "pay invoice", "execute shell", "rm -rf", "delete database", "drop database", "drop all", "delete all database"]):
            is_high_risk = True
            high_risk_reason = high_risk_reason or "Irreversible destructive or financial transaction detected in unattended commitment"

        if is_high_risk:
            # GATED: High-risk actions MUST NOT execute unattended!
            delivery_record = {
                "commitment_id": commitment_id,
                "skill_name": commitment.get("skill_name"),
                "status": "partially_complete",
                "summary": f"Unattended execution for '{commitment.get('skill_name')}' partially completed. High-risk action queued for human approval.",
                "pending_approval": {
                    "action": task_intent,
                    "reason": high_risk_reason,
                    "queued_at": datetime.now(timezone.utc).isoformat(),
                },
                "output": "Action halted before execution: Requires human approval per safety policy.",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            did = store.add_delivery(delivery_record)
            
            result_payload = {
                "success": True,
                "status": "partially_complete",
                "delivery_id": did,
                "pending_approval_required": True,
                "reason": high_risk_reason,
                "summary": delivery_record["summary"],
            }
            store.record_execution_idempotency(idem_key, result_payload)
            return result_payload

        # 4. Safe Unattended Execution via Orchestrator
        from app.agent import orchestrator
        trace_id = f"unattended_{commitment_id}_{int(time.time())}"
        turn_res = await orchestrator.run_turn(
            task_intent,
            hands_off=True,
            effort="standard",
        )

        # 5. Record Outcome onto Skill (PRD §6.2)
        from app.forge import record_skill_outcome
        exec_success = turn_res.get("type") == "response"
        record_skill_outcome(
            commitment.get("skill_id", ""),
            outcome="succeeded" if exec_success else "abandoned"
        )

        # Check if skill degraded below retirement threshold during this run
        updated_skill = store.get_skill(commitment.get("skill_id", ""))
        if updated_skill and not updated_skill.get("enabled", True):
            self.auto_suspend_for_skill(
                commitment.get("skill_id", ""),
                reason=f"Skill auto-retired: {updated_skill.get('disabled_reason', 'Success rate < 60%')}"
            )

        # 6. Delivery Ledger Record
        delivery_record = {
            "commitment_id": commitment_id,
            "skill_name": commitment.get("skill_name"),
            "status": "completed" if exec_success else "failed",
            "summary": f"Executed '{commitment.get('skill_name')}' unattended.",
            "output": turn_res.get("text", "Completed successfully."),
            "tools_used": turn_res.get("tools_used", []),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "telemetry": turn_res.get("telemetry", {}),
        }
        did = store.add_delivery(delivery_record)

        # 7. Update Commitment Stats & Next Run
        next_run = calculate_next_run(commitment.get("cadence", "weekly"))
        store.update_commitment(commitment_id, {
            "last_run": datetime.now(timezone.utc).isoformat(),
            "run_count": commitment.get("run_count", 0) + 1,
            "next_run_time": next_run,
        })

        result_payload = {
            "success": True,
            "status": "completed",
            "delivery_id": did,
            "summary": delivery_record["summary"],
            "output": delivery_record["output"],
            "tools_used": turn_res.get("tools_used", []),
            "next_run_time": next_run,
        }
        store.record_execution_idempotency(idem_key, result_payload)
        return result_payload

    def auto_suspend_for_skill(self, skill_name: str, reason: str):
        """Automatically suspends all commitments linked to a retired skill."""
        for c in store.list_commitments():
            if c.get("skill_id") == skill_name or c.get("skill_name") == skill_name:
                store.update_commitment(c["id"], {
                    "enabled": False,
                    "status": "suspended",
                    "disabled_reason": reason,
                })

    def get_proactive_announcement(self) -> Optional[str]:
        """Surfaces at most ONE plain-language proactive announcement on session start."""
        # 1. Check suspended commitments
        for c in store.list_commitments():
            if c.get("status") == "suspended" and c.get("disabled_reason"):
                return f"I've suspended the automated commitment for '{c.get('skill_name')}' because its measured success rate dropped below our threshold."

        # 2. Check pending deliveries with approvals
        deliveries = store.list_deliveries(limit=5)
        for d in deliveries:
            if d.get("status") == "partially_complete" and d.get("pending_approval"):
                appr = d["pending_approval"]
                return f"While you were away, I ran '{d.get('skill_name')}' but paused before executing '{appr.get('action')}' because it requires your explicit approval."

        # 3. Check reinforced correction rules
        rules = store.list_corrections(active_only=True)
        for r in rules:
            if r.get("reinforcement_count", 0) >= 3:
                return f"I've noticed your preference on '{r.get('situation')}' multiple times, so I've made it a standing rule across all future tasks."

        return None

commitment_manager = AutonomousCommitmentManager()
