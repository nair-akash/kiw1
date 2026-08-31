import pytest
from datetime import datetime, timedelta, timezone
from app.commitments import (
    calculate_next_run,
    commitment_manager,
    infer_cadence_from_history,
)
from app.forge import forge_skill, record_skill_outcome
from app.store import store

def test_cadence_inference_code():
    store.reset_for_benchmark()
    now = datetime.now(timezone.utc)
    
    # Simulate daily occurrences in fingerprints
    fp = "test_daily_fp"
    store.add_fingerprint(fp, "daily status update", ["standard_reasoning"])
    store.add_fingerprint(fp, "daily status update", ["standard_reasoning"])
    
    cadence, cron, human = infer_cadence_from_history(fp)
    assert cadence in ["daily", "weekly"]
    assert "0 9 * * " in cron

def test_commitment_creation_provenance():
    store.reset_for_benchmark()
    skill = forge_skill("Audit quarterly cloud compute budget", ["standard_reasoning"], name="skill-cloud-audit")
    
    cmt = commitment_manager.create_commitment("skill-cloud-audit")
    assert cmt["skill_name"] == "skill-cloud-audit"
    assert cmt["provenance"] == "agent_self_derived"
    assert cmt["status"] == "active"
    assert cmt["enabled"] is True
    assert "next_run_time" in cmt
    
    # Verified in store
    retrieved = store.get_commitment(cmt["id"])
    assert retrieved is not None
    assert retrieved["provenance"] == "agent_self_derived"

@pytest.mark.asyncio
async def test_unattended_execution_low_risk():
    store.reset_for_benchmark()
    skill = forge_skill("Summarize project roadmap status", ["standard_reasoning"], name="skill-roadmap")
    cmt = commitment_manager.create_commitment("skill-roadmap")
    
    # Execute unattended
    res = await commitment_manager.execute_commitment(cmt["id"], force=True)
    assert res["success"] is True
    assert res["status"] == "completed"
    assert "delivery_id" in res
    
    # Check delivery ledger
    deliveries = store.list_deliveries()
    assert len(deliveries) >= 1
    assert deliveries[0]["skill_name"] == "skill-roadmap"
    assert deliveries[0]["status"] == "completed"

@pytest.mark.asyncio
async def test_unattended_execution_high_risk_gated():
    """PRD §6.7 & §12b: High risk destructive/financial actions MUST NOT execute
    unattended. They must queue for approval and report status partially_complete.
    """
    store.reset_for_benchmark()
    skill = forge_skill("Delete all database backup records and drop table", ["standard_reasoning"], name="skill-drop-table")
    cmt = commitment_manager.create_commitment("skill-drop-table")
    
    # Execute unattended
    res = await commitment_manager.execute_commitment(cmt["id"], force=True)
    assert res["success"] is True
    assert res["status"] == "partially_complete"
    assert res["pending_approval_required"] is True
    
    # Verify queued in delivery ledger
    deliveries = store.list_deliveries()
    assert len(deliveries) >= 1
    assert deliveries[0]["status"] == "partially_complete"
    assert "pending_approval" in deliveries[0]
    assert "approval" in deliveries[0]["pending_approval"]["reason"].lower() or "transaction" in deliveries[0]["pending_approval"]["reason"].lower() or "destructive" in deliveries[0]["pending_approval"]["reason"].lower()

@pytest.mark.asyncio
async def test_idempotency_prevents_double_execution():
    """PRD §6.8: Pub/Sub redeliveries with identical idempotency key must not double-execute."""
    store.reset_for_benchmark()
    skill = forge_skill("Fetch latest market news", ["standard_reasoning"], name="skill-news")
    cmt = commitment_manager.create_commitment("skill-news")
    
    idem_key = "test_redelivery_key_123"
    
    # Run 1: First execution
    res1 = await commitment_manager.execute_commitment(cmt["id"], idempotency_key=idem_key)
    assert res1["success"] is True
    assert res1.get("idempotent_duplicate") is not True
    del_count_1 = len(store.list_deliveries())
    
    # Run 2: Redelivered execution with same idempotency key
    res2 = await commitment_manager.execute_commitment(cmt["id"], idempotency_key=idem_key)
    assert res2["success"] is True
    assert res2.get("idempotent_duplicate") is True
    del_count_2 = len(store.list_deliveries())
    
    # Did not duplicate execution in delivery ledger
    assert del_count_1 == del_count_2

def test_skill_retirement_auto_suspends_commitment():
    """Closing the loop: When a skill auto-disables on low success rate,
    its commitment must auto-suspend itself immediately.
    """
    store.reset_for_benchmark()
    skill = forge_skill("Unreliable web scraper", ["web_search"], name="skill-unreliable")
    cmt = commitment_manager.create_commitment("skill-unreliable")
    
    assert store.get_commitment(cmt["id"])["status"] == "active"
    
    # Drive skill below success threshold (5 consecutive failures)
    for _ in range(5):
        record_skill_outcome("skill-unreliable", "abandoned")
    
    updated_skill = store.get_skill("skill-unreliable")
    assert updated_skill["enabled"] is False
    
    # Commitment must be suspended automatically
    updated_cmt = store.get_commitment(cmt["id"])
    assert updated_cmt["status"] == "suspended"
    assert updated_cmt["enabled"] is False
    assert "Auto-disabled" in updated_cmt["disabled_reason"]

def test_proactive_surfacing_on_session_start():
    store.reset_for_benchmark()
    skill = forge_skill("Failing background process", ["web_search"], name="skill-failing")
    cmt = commitment_manager.create_commitment("skill-failing")
    
    # Auto-suspend
    for _ in range(5):
        record_skill_outcome("skill-failing", "abandoned")
        
    announcement = commitment_manager.get_proactive_announcement()
    assert announcement is not None
    assert "suspended the automated commitment" in announcement
    assert "skill-failing" in announcement
