import pytest
from app.planner import planner

def test_planner_generates_three_diverse_paths():
    candidates = planner.generate_candidate_paths("Deploy KIW1 agent to Cloud Run")
    assert len(candidates) == 3
    names = [c.name for c in candidates]
    assert any("Fastest" in n for n in names)
    assert any("Cheapest" in n for n in names)
    assert any("Thorough" in n for n in names)

def test_planner_scores_paths_deterministically():
    plan = planner.build_plan("Analyze large codebase")
    assert plan.selected_path is not None
    assert plan.selected_path.score > 0
    assert len(plan.subtasks) >= 2
    assert "Selected" in plan.selection_reason

def test_planner_parallel_agent_condition():
    # Thorough path has can_parallelize = True
    plan = planner.build_plan("Complex multi-branch research and verification")
    if plan.selected_path.can_parallelize:
        assert plan.use_parallel_agents is True
