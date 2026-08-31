import pytest
from app.plugins.base import BasePlugin, PluginManifest, ToolEffect
from app.plugins.kernel import Kernel, KernelError

class SamplePluginA(BasePlugin):
    def __init__(self):
        manifest = PluginManifest(
            name="plugin_a",
            provides_tools=["tool_a"],
            effects={"tool_a": ToolEffect(reversible=True, risk="none")},
        )
        super().__init__(manifest)

    def get_tools(self):
        return {"tool_a": lambda x: f"result_{x}"}

class SamplePluginB(BasePlugin):
    def __init__(self):
        manifest = PluginManifest(
            name="plugin_b",
            requires=["plugin_a"],
            provides_tools=["tool_b"],
        )
        super().__init__(manifest)

def test_kernel_plugin_registration_and_dependencies():
    k = Kernel()
    pa = SamplePluginA()
    pb = SamplePluginB()

    # Registering B before dependency A raises KernelError
    with pytest.raises(KernelError):
        k.register_plugin(pb)

    # Register A then B succeeds
    k.register_plugin(pa)
    k.register_plugin(pb)
    assert len(k.list_plugins()) == 2

    # Unregistering A while B depends on it raises KernelError
    with pytest.raises(KernelError):
        k.unregister_plugin("plugin_a")

def test_kernel_tool_execution():
    k = Kernel()
    pa = SamplePluginA()
    k.register_plugin(pa)

    res = k.execute_tool("tool_a", x="test")
    assert res == "result_test"
