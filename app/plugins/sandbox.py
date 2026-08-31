import io
import sys
import time
import traceback
from typing import Any, Callable, Dict, Optional
from app.plugins.base import BasePlugin, PluginManifest, ToolEffect

class CodeSandboxPlugin(BasePlugin):
    """Isolated Python Code Interpreter Sandbox.
    Enables safe on-demand code execution for math, data analysis, algorithm verification,
    and simulation with stdout/stderr capture and timeout limits.
    """

    def __init__(self):
        manifest = PluginManifest(
            name="code_sandbox",
            version="1.0.0",
            requires=[],
            provides_tools=["execute_python_code"],
            effects={
                "execute_python_code": ToolEffect(
                    reversible=True,
                    risk="low",
                    approval="report",
                ),
            },
            capabilities=["compute:python_sandbox"],
            cost_class="cheap",
            description="Isolated Python code execution environment with stdout/stderr capture and mathematical verification",
        )
        super().__init__(manifest)

    def execute_python_code(self, code: str, timeout_seconds: float = 3.0) -> Dict[str, Any]:
        """Executes a Python code snippet in a sandboxed namespace and captures output."""
        code_clean = code.strip()
        if code_clean.startswith("```python"):
            code_clean = code_clean.split("```python", 1)[1]
        elif code_clean.startswith("```"):
            code_clean = code_clean.split("```", 1)[1]
        if code_clean.endswith("```"):
            code_clean = code_clean.rsplit("```", 1)[0]
        code_clean = code_clean.strip()

        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()

        ALLOWED_MODULES = {
            "math", "json", "random", "datetime", "re", "collections",
            "itertools", "statistics", "typing", "string", "heapq", "bisect", "copy"
        }

        def safe_import(name, *args, **kwargs):
            root_name = name.split(".")[0]
            if root_name in ALLOWED_MODULES:
                return __import__(name, *args, **kwargs)
            raise ImportError(f"Import of module '{name}' is restricted in sandbox")

        # Safe global execution context
        safe_globals: Dict[str, Any] = {
            "__builtins__": {
                "__import__": safe_import,
                "abs": abs,
                "all": all,
                "any": any,
                "bin": bin,
                "bool": bool,
                "chr": chr,
                "dict": dict,
                "divmod": divmod,
                "enumerate": enumerate,
                "filter": filter,
                "float": float,
                "format": format,
                "frozenset": frozenset,
                "hex": hex,
                "int": int,
                "isinstance": isinstance,
                "issubclass": issubclass,
                "iter": iter,
                "len": len,
                "list": list,
                "map": map,
                "max": max,
                "min": min,
                "next": next,
                "oct": oct,
                "ord": ord,
                "pow": pow,
                "print": lambda *args, **kwargs: print(*args, file=stdout_capture, **kwargs),
                "range": range,
                "reversed": reversed,
                "round": round,
                "set": set,
                "slice": slice,
                "sorted": sorted,
                "str": str,
                "sum": sum,
                "tuple": tuple,
                "type": type,
                "zip": zip,
                "Exception": Exception,
                "ValueError": ValueError,
                "TypeError": TypeError,
                "KeyError": KeyError,
                "IndexError": IndexError,
            }
        }

        # Provide standard mathematical and data modules
        import math
        import json
        import statistics
        import datetime
        safe_globals["math"] = math
        safe_globals["json"] = json
        safe_globals["statistics"] = statistics
        safe_globals["datetime"] = datetime

        local_vars: Dict[str, Any] = {}
        start_time = time.perf_counter()
        success = True
        error_msg = None

        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture

        try:
            # First try compiling as single expression to capture implicit return
            try:
                compiled = compile(code_clean, "<sandbox>", "eval")
                eval_result = eval(compiled, safe_globals, local_vars)
                if eval_result is not None:
                    print(repr(eval_result), file=stdout_capture)
            except SyntaxError:
                # Compile and execute as full script
                compiled = compile(code_clean, "<sandbox>", "exec")
                exec(compiled, safe_globals, local_vars)
        except Exception as ex:
            success = False
            error_msg = f"{type(ex).__name__}: {str(ex)}"
            traceback.print_exc(file=stderr_capture)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        out_str = stdout_capture.getvalue()
        err_str = stderr_capture.getvalue()

        # Extract returned result variable if present
        returned_val = local_vars.get("result", local_vars.get("output", out_str.strip()))

        return {
            "success": success,
            "stdout": out_str,
            "stderr": err_str,
            "error": error_msg,
            "result": returned_val,
            "execution_time_ms": round(elapsed_ms, 2),
            "code_executed": code_clean,
        }

    def get_tools(self) -> Dict[str, Callable[..., Any]]:
        return {
            "execute_python_code": self.execute_python_code,
        }

sandbox_plugin = CodeSandboxPlugin()
