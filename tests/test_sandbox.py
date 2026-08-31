import pytest
from app.plugins.sandbox import sandbox_plugin

def test_sandbox_plugin_manifest():
    assert "execute_python_code" in sandbox_plugin.manifest.provides_tools
    assert sandbox_plugin.manifest.effects["execute_python_code"].risk == "low"

def test_execute_simple_math():
    code = "result = sum([x**2 for x in range(1, 11)])"
    res = sandbox_plugin.execute_python_code(code)
    assert res["success"] is True
    assert res["result"] == 385
    assert res["execution_time_ms"] >= 0

def test_execute_stdout_capture():
    code = """
for i in range(3):
    print(f"Count: {i}")
"""
    res = sandbox_plugin.execute_python_code(code)
    assert res["success"] is True
    assert "Count: 0" in res["stdout"]
    assert "Count: 2" in res["stdout"]

def test_execute_handles_exceptions_cleanly():
    code = "1 / 0"
    res = sandbox_plugin.execute_python_code(code)
    assert res["success"] is False
    assert "ZeroDivisionError" in res["error"]

def test_execute_markdown_strip():
    code = "```python\nresult = 42 * 2\n```"
    res = sandbox_plugin.execute_python_code(code)
    assert res["success"] is True
    assert res["result"] == 84

def test_execute_safe_module_imports():
    code = """
import math
import json
data = json.dumps({"pi": round(math.pi, 2)})
print(data)
result = data
"""
    res = sandbox_plugin.execute_python_code(code)
    assert res["success"] is True
    assert '{"pi": 3.14}' in res["stdout"]

def test_execute_blocks_unsafe_imports():
    code = "import os\nos.listdir('.')"
    res = sandbox_plugin.execute_python_code(code)
    assert res["success"] is False
    assert "restricted" in res["error"]

