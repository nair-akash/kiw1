from typing import Any, Dict, Optional
from app.plugins.base import RiskLevel, ToolEffect

class ApprovalLayer:
    """Manifest-driven Approval Layer.
    Risk is structural from plugin manifests — never estimated by an LLM.
    """

    def __init__(self, hands_off: bool = False):
        self.hands_off = hands_off

    def check_approval(self, tool_name: str, effect: ToolEffect, params: Optional[Dict[str, Any]] = None) -> tuple[bool, str]:
        """Returns (requires_explicit_user_approval, rationale)."""
        risk = effect.risk

        # HIGH RISK: Irreversible, financial, external sends
        # Rule: High risk ALWAYS requires explicit user approval. Hands-off mode CANNOT silence high risk.
        if risk == "high":
            return True, f"HIGH RISK: '{tool_name}' involves irreversible or external actions and requires explicit approval."

        # MEDIUM RISK: Costly or hard to reverse
        if risk == "medium":
            if self.hands_off:
                return False, f"MEDIUM RISK: '{tool_name}' auto-approved under hands-off mode."
            return True, f"MEDIUM RISK: '{tool_name}' requires confirmation (default: approve)."

        # LOW RISK: Reversible external
        if risk == "low":
            return False, f"LOW RISK: '{tool_name}' executed; action reported to user."

        # NONE: Local reversible
        return False, f"NO RISK: '{tool_name}' executed silently."

    def classify_risk(self, task_intent: str, tool_name: str) -> tuple[str, str]:
        """Classifies risk level for an intent and tool name deterministically."""
        intent_lower = task_intent.lower()
        if any(w in intent_lower for w in ["delete all", "drop table", "wire funds", "pay invoice", "execute shell", "rm -rf", "delete database", "drop database"]):
            return "HIGH", "Irreversible destructive or financial transaction detected in task intent."

        from app.plugins.kernel import kernel
        manifest = kernel.get_manifest(tool_name) if hasattr(kernel, "get_manifest") else None
        if manifest and getattr(manifest, "risk", "") == "high":
            return "HIGH", f"Tool '{tool_name}' is registered as HIGH risk in plugin manifest."
        elif manifest and getattr(manifest, "risk", "") == "medium":
            return "MEDIUM", f"Tool '{tool_name}' is registered as MEDIUM risk."

        return "LOW", "Standard non-destructive operation."

approval_layer = ApprovalLayer(hands_off=False)
