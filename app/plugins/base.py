from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Literal, Optional

RiskLevel = Literal["none", "low", "medium", "high"]
ApprovalRequirement = Literal["never", "report", "ask", "always"]
CostClass = Literal["cheap", "standard", "expensive"]

@dataclass
class ToolEffect:
    reversible: bool = True
    risk: RiskLevel = "none"
    approval: ApprovalRequirement = "never"
    undo_handler: Optional[Callable[..., Any]] = None

@dataclass
class PluginManifest:
    name: str
    version: str = "1.0.0"
    requires: List[str] = field(default_factory=list)
    provides_tools: List[str] = field(default_factory=list)
    effects: Dict[str, ToolEffect] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    cost_class: CostClass = "cheap"
    description: str = ""

class BasePlugin:
    def __init__(self, manifest: PluginManifest):
        self.manifest = manifest
        self.enabled = True

    def get_tools(self) -> Dict[str, Callable[..., Any]]:
        """Returns map of tool_name -> callable."""
        return {}

    def on_load(self):
        pass

    def on_unload(self):
        pass
