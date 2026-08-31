import pytest
from app.ledger import ledger
from app.store import store

def test_correction_recording_and_retrieval():
    store.reset_for_benchmark()
    rec = ledger.record_correction(
        situation="generating JSON responses",
        wrong_action="wrapping in markdown code fences",
        correction="always return raw JSON without backticks",
    )
    assert rec["id"].startswith("rule_")

    matches = ledger.find_relevant_rules("generate JSON response for user profile")
    assert len(matches) > 0
    assert "raw JSON" in matches[0]["rule"]

def test_rule_reinforcement():
    store.reset_for_benchmark()
    rec = ledger.record_correction(
        situation="formatting dates",
        wrong_action="using MM/DD/YYYY",
        correction="use ISO YYYY-MM-DD",
    )
    rule_id = rec["id"]
    updated = ledger.reinforce_rule(rule_id)
    assert updated["weight"] == 1.2
    assert updated["reinforcement_count"] == 1

def test_rule_contradiction_retirement():
    store.reset_for_benchmark()
    rec = ledger.record_correction(
        situation="drafting messages",
        wrong_action="using formal tone",
        correction="use casual tone",
    )
    rule_id = rec["id"]

    # 1st contradiction
    ledger.record_contradiction(rule_id)
    rules = ledger.list_rules()
    target = next(r for r in rules if r["id"] == rule_id)
    assert target["active"] is True

    # 2nd contradiction triggers auto-retirement
    ledger.record_contradiction(rule_id)
    rules = ledger.list_rules()
    target = next(r for r in rules if r["id"] == rule_id)
    assert target["active"] is False
    assert "Auto-retired" in target["retired_reason"]
