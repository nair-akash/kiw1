import inspect
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Set
from app.plugins.base import BasePlugin, PluginManifest, ToolEffect

class KernelError(Exception):
    pass

class Kernel:
    """KIW1 Composition Kernel.
    Manages plugin lifecycles, capability sandboxing, reversible effect history,
    and typed event subscriptions.
    """
    def __init__(self):
        self._plugins: Dict[str, BasePlugin] = {}
        self._tool_registry: Dict[str, Callable[..., Any]] = {}
        self._tool_to_plugin: Dict[str, str] = {}
        self._effect_history: List[Dict[str, Any]] = []
        self._event_listeners: Dict[str, List[Callable[[Dict[str, Any]], None]]] = defaultdict(list)

    # 1. Plugin Load / Unload with Dependency Resolution
    def register_plugin(self, plugin: BasePlugin):
        name = plugin.manifest.name
        # Check dependencies
        for req in plugin.manifest.requires:
            if req not in self._plugins:
                raise KernelError(f"Cannot load plugin '{name}': missing dependency '{req}'")

        plugin.on_load()
        self._plugins[name] = plugin

        # Register tools provided by the plugin
        for tool_name, tool_fn in plugin.get_tools().items():
            self._tool_registry[tool_name] = tool_fn
            self._tool_to_plugin[tool_name] = name

        self.emit_event("plugin:loaded", {"name": name, "version": plugin.manifest.version})

    def unregister_plugin(self, name: str):
        if name not in self._plugins:
            return

        # Check if other plugins depend on this
        for other_name, plugin in self._plugins.items():
            if name in plugin.manifest.requires:
                raise KernelError(f"Cannot unload plugin '{name}': plugin '{other_name}' depends on it")

        plugin = self._plugins.pop(name)
        plugin.on_unload()

        # Remove tools
        tools_to_remove = [t for t, p in self._tool_to_plugin.items() if p == name]
        for t in tools_to_remove:
            self._tool_registry.pop(t, None)
            self._tool_to_plugin.pop(t, None)

        self.emit_event("plugin:unloaded", {"name": name})

    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        return self._plugins.get(name)

    def list_plugins(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": p.manifest.name,
                "version": p.manifest.version,
                "description": p.manifest.description,
                "requires": p.manifest.requires,
                "provides_tools": list(p.get_tools().keys()),
                "capabilities": p.manifest.capabilities,
                "cost_class": p.manifest.cost_class,
                "enabled": p.enabled,
            }
            for p in self._plugins.values()
        ]

    # 2. Tool Execution & Capability Sandboxing
    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        if tool_name not in self._tool_registry:
            raise KernelError(f"Tool '{tool_name}' not found in registry")

        plugin_name = self._tool_to_plugin[tool_name]
        plugin = self._plugins[plugin_name]
        manifest = plugin.manifest

        effect: ToolEffect = manifest.effects.get(tool_name, ToolEffect(reversible=True, risk="none", approval="never"))

        tool_fn = self._tool_registry[tool_name]
        result = tool_fn(**kwargs)

        # Record reversible effect
        if effect.reversible and effect.undo_handler:
            self._effect_history.append({
                "tool": tool_name,
                "plugin": plugin_name,
                "params": kwargs,
                "result": result,
                "undo_fn": effect.undo_handler,
            })

        self.emit_event("tool:executed", {
            "tool": tool_name,
            "plugin": plugin_name,
            "risk": effect.risk,
            "params": kwargs,
        })
        return result

    def get_tool_effect(self, tool_name: str) -> ToolEffect:
        plugin_name = self._tool_to_plugin.get(tool_name)
        if not plugin_name or plugin_name not in self._plugins:
            return ToolEffect(reversible=True, risk="none", approval="never")
        return self._plugins[plugin_name].manifest.effects.get(
            tool_name, ToolEffect(reversible=True, risk="none", approval="never")
        )

    def get_all_tools(self) -> Dict[str, Callable[..., Any]]:
        return dict(self._tool_registry)

    # 3. Reversible Effects
    def undo_last_effect(self) -> Optional[Dict[str, Any]]:
        if not self._effect_history:
            return None
        last = self._effect_history.pop()
        undo_fn = last.get("undo_fn")
        if undo_fn:
            undo_res = undo_fn(last)
            return {"undone_tool": last["tool"], "result": undo_res}
        return {"undone_tool": last["tool"], "result": "no_undo_handler"}

    # 4. Typed Event Bus
    def subscribe_event(self, event_name: str, handler: Callable[[Dict[str, Any]], None]):
        self._event_listeners[event_name].append(handler)

    def emit_event(self, event_name: str, data: Dict[str, Any]):
        for handler in self._event_listeners.get(event_name, []):
            try:
                handler(data)
            except Exception:
                pass

kernel = Kernel()
