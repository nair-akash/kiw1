import pytest
import asyncio
from evals.frontier_benchmarks import frontier_runner

def test_frontier_tasks_loaded():
    assert len(frontier_runner.tasks) >= 35
    categories = {t["category"] for t in frontier_runner.tasks}
    assert "hle" in categories
    assert "gpqa" in categories
    assert "math_500" in categories
    assert "swe_bench" in categories

@pytest.mark.asyncio
async def test_evaluate_sandbox_task():
    task = {
        "id": "test_swe",
        "category": "swe_bench",
        "assertion_type": "sandbox_exec",
        "code": "result = sum([x for x in range(10) if x % 2 == 0])",
        "expected_result": 20
    }
    passed, detail, output = await frontier_runner.evaluate_task(task)
    assert passed is True
    assert "matches expected 20" in detail

@pytest.mark.asyncio
async def test_evaluate_math_task():
    task = {
        "id": "test_math",
        "category": "math_500",
        "assertion_type": "output_contains",
        "assertion_value": "44",
        "expected_keywords": ["44", "derangement"],
        "prompt": "Calculate D_5, the number of derangements of 5 elements."
    }
    passed, detail, text = await frontier_runner.evaluate_task(task)
    assert passed is True
    assert "44" in text or "derangement" in text.lower()
