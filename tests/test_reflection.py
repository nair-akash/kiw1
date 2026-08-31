import pytest
from app.reflection import reflector

@pytest.mark.asyncio
async def test_reflection_3_phase_execution():
    res = await reflector.reflect_and_reason(
        prompt="Design a deterministic state cache with TTL eviction.",
        system_prefix="You are KIW1, a principal systems architect.",
        context_details=["Requirement: Thread-safe in-memory cache."],
    )
    assert "final_text" in res
    assert "draft_text" in res
    assert "critique_text" in res
    assert res["phases_executed"] == 3
    assert res["confidence"] >= 0.85
    assert len(res["audit_trail"]) == 3
