import pytest
from app.router import router

def test_model_router_effort_mapping():
    model_thorough, budget_thorough = router.route("general", "thorough")
    assert budget_thorough >= 4096

    model_quick, budget_quick = router.route("general", "quick")
    assert budget_quick == 0

    model_std, budget_std = router.route("general", "standard")
    assert budget_std > 0

@pytest.mark.asyncio
async def test_router_generate_response():
    res = await router.generate_response(
        prompt="Explain quantum entanglement briefly.",
        effort="quick",
        task_type="classification",
    )
    assert "text" in res
    assert "model" in res
    assert "total_tokens" in res or "prompt_tokens" in res
    assert res.get("total_tokens", 0) > 0 or res.get("prompt_tokens", 0) > 0
