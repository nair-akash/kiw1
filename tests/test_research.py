import pytest
from app.research import OvernightResearchLoop

def test_research_target_selection():
    loop = OvernightResearchLoop()
    topic, reason, category = loop.select_research_target()
    assert topic is not None
    assert len(topic) > 0
    assert reason is not None
    assert category in ["correction_grounding", "memory_refresh", "capability_grounding"]

@pytest.mark.asyncio
async def test_execute_research_cycle():
    loop = OvernightResearchLoop()
    report = await loop.execute_research_cycle()
    assert "target_topic" in report
    assert "survived_findings" in report
    assert "summary" in report
    assert report["status"] == "completed"
