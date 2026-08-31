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

@pytest.mark.asyncio
async def test_router_handles_multimodal_attachments():
    import base64
    fake_png_base64 = base64.b64encode(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82").decode("utf-8")
    attachments = [{
        "name": "diagram.png",
        "mime_type": "image/png",
        "data": fake_png_base64
    }]
    res = await router.generate_response(
        prompt="Analyze this diagram.",
        effort="quick",
        attachments=attachments,
    )
    assert "text" in res
    assert res.get("model") is not None
