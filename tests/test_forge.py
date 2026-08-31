import pytest
from app.forge import (
    fingerprint,
    forge_skill,
    record_skill_outcome,
    record_task_execution,
    should_promote,
)
from app.store import store

def test_fingerprint_stability_across_phrasing():
    a = fingerprint("chase the unpaid invoices", ["search_mail"])
    b = fingerprint("Please chase my unpaid invoices!", ["search_mail"])
    assert a == b

def test_fingerprint_differs_on_tools():
    a = fingerprint("chase the unpaid invoices", ["search_mail"])
    b = fingerprint("chase the unpaid invoices", ["send_email"])
    assert a != b

def test_skill_forge_threshold_trigger():
    store.reset_for_benchmark()
    tools = ["calculate", "remember"]
    intent = "audit monthly billing report"
    
    fp = fingerprint(intent, tools)
    assert not should_promote(fp)

    record_task_execution(intent, tools)
    assert not should_promote(fp)

    record_task_execution(intent, tools)
    assert not should_promote(fp)

    record_task_execution(intent, tools)
    assert should_promote(fp)

def test_skill_auto_retirement_below_threshold():
    store.reset_for_benchmark()
    skill = forge_skill("scrape unverified news", ["web_search"], name="test-scraper-skill")
    
    # 4 runs (provisional state)
    for _ in range(4):
        record_skill_outcome("test-scraper-skill", "abandoned")
    
    skill = store.get_skill("test-scraper-skill")
    assert skill["provisional"] is True
    assert skill["enabled"] is True

    # 5th run triggers auto-retirement check (<60% success)
    record_skill_outcome("test-scraper-skill", "abandoned")
    skill = store.get_skill("test-scraper-skill")
    assert skill["provisional"] is False
    assert skill["enabled"] is False
    assert "Auto-disabled" in skill["disabled_reason"]
