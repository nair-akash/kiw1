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

@pytest.mark.asyncio
async def test_three_identical_requests_through_orchestrator():
    """Verifies that 3 identical requests through the REAL orchestrator.run_turn
    entry point triggers the Skill Forge announcement on the 3rd turn and not before,
    and registers the forged skill in the registry.
    """
    from app.agent import orchestrator
    store.reset_for_benchmark()
    
    prompt = "Compute 45 * 12 + 100"
    
    # Turn 1
    res1 = await orchestrator.run_turn(prompt, hands_off=True)
    assert res1["forged_skill"] is None
    assert len(store.list_skills()) == 0
    
    # Turn 2
    res2 = await orchestrator.run_turn(prompt, hands_off=True)
    assert res2["forged_skill"] is None
    assert len(store.list_skills()) == 0
    
    # Turn 3: Triggers auto-forging
    res3 = await orchestrator.run_turn(prompt, hands_off=True)
    assert res3["forged_skill"] is not None
    assert "three times this week" in res3["forged_skill"]["message"]
    
    # Verify skill is in registry
    skill_name = res3["forged_skill"]["skill_name"]
    skills = store.list_skills()
    assert any(s["name"] == skill_name for s in skills)
    
    # Turn 4: Already forged, should not announce again
    res4 = await orchestrator.run_turn(prompt, hands_off=True)
    assert res4["forged_skill"] is None

@pytest.mark.asyncio
async def test_differently_worded_requests_reach_forge_threshold():
    """Verifies that differently worded requests with identical normalized intent
    reach the threshold and forge a skill via orchestrator.run_turn.
    """
    from app.agent import orchestrator
    store.reset_for_benchmark()
    
    # Turn 1
    res1 = await orchestrator.run_turn("audit the quarterly cloud compute budget", hands_off=True)
    assert res1["forged_skill"] is None
    
    # Turn 2
    res2 = await orchestrator.run_turn("Please audit my quarterly cloud compute budget!", hands_off=True)
    assert res2["forged_skill"] is None
    
    # Turn 3
    res3 = await orchestrator.run_turn("audit quarterly cloud compute budget", hands_off=True)
    assert res3["forged_skill"] is not None
    assert "three times this week" in res3["forged_skill"]["message"]

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
