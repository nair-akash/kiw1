import pytest
from app.swarm import swarm_orchestrator

def test_swarm_agent_registration():
    assert len(swarm_orchestrator.agents) == 4
    names = [a.name for a in swarm_orchestrator.agents]
    assert "Architect" in names
    assert "Security Auditor" in names
    assert "Research Analyst" in names
    assert "Memory Custodian" in names

@pytest.mark.asyncio
async def test_swarm_orchestration_execution():
    res = await swarm_orchestrator.orchestrate_swarm("Design a zero-trust API gateway.")
    assert "task" in res
    assert "consensus" in res
    assert len(res["swarm_results"]) == 4
    assert res["agent_count"] == 4
    assert res["elapsed_ms"] >= 0
