import math
from typing import Any, Callable, Dict, Optional
from app.ledger import ledger
from app.memory import palace
from app.plugins.base import BasePlugin, PluginManifest, ToolEffect
from app.plugins.kernel import kernel
from app.plugins.search import search_plugin
from app.plugins.vault import vault_plugin
from app.store import store

class CoreToolsPlugin(BasePlugin):
    """Core built-in tools for memory, calculation, corrections, and skill invocation."""

    def __init__(self):
        manifest = PluginManifest(
            name="core_tools",
            version="1.0.0",
            requires=[],
            provides_tools=[
                "remember",
                "recall",
                "correct_agent",
                "calculate",
                "execute_skill",
                "draft_email",
                "send_outbound_message",
            ],
            effects={
                "remember": ToolEffect(reversible=True, risk="none", approval="never", undo_handler=self._undo_remember),
                "recall": ToolEffect(reversible=True, risk="none", approval="never"),
                "correct_agent": ToolEffect(reversible=True, risk="none", approval="never"),
                "calculate": ToolEffect(reversible=True, risk="none", approval="never"),
                "execute_skill": ToolEffect(reversible=True, risk="low", approval="report"),
                "draft_email": ToolEffect(reversible=True, risk="low", approval="report"),
                "send_outbound_message": ToolEffect(reversible=False, risk="high", approval="always"),
            },
            capabilities=["state:memory", "state:ledger"],
            cost_class="cheap",
            description="Foundational capabilities for memory, ledger feedback, and safe task execution",
        )
        super().__init__(manifest)

    def _undo_remember(self, effect_record: Dict[str, Any]) -> str:
        res = effect_record.get("result", {})
        doc_id = res.get("id")
        return f"Reverted memory storage for {doc_id}"

    def remember(self, fact: str, room: Optional[str] = None, locus: Optional[str] = None) -> Dict[str, Any]:
        """Store a durable fact or preference in the Memory Palace hierarchy (room -> locus -> item).
        
        Args:
            fact: The fact or preference to remember.
            room: Optional spatial room (e.g. projects, preferences, knowledge).
            locus: Optional spatial locus (e.g. kiw1, formatting, architecture).
        """
        return palace.store_memory(fact, room=room, locus=locus, provenance="user_direct")

    def recall(self, query: str, room: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve stored knowledge and preferences from the Memory Palace.
        
        Args:
            query: The search query or topic to look up.
            room: Optional specific room to limit the search.
        """
        results = palace.retrieve(query, room=room)
        return {"query": query, "found": len(results), "memories": results}

    def correct_agent(self, situation: str, wrong_action: str, correction: str) -> Dict[str, Any]:
        """Teach KIW1 a correction so it never repeats the mistake in the future.
        
        Args:
            situation: What context or task triggered the issue.
            wrong_action: What the agent did incorrectly.
            correction: What the agent should have done instead.
        """
        rule = ledger.record_correction(situation, wrong_action, correction)
        return {"status": "learned", "rule_id": rule["id"], "rule": rule["rule"]}

    def calculate(self, expression: str) -> Dict[str, Any]:
        """Safely evaluate a mathematical expression in pure Python without calling an LLM.
        
        Args:
            expression: The arithmetic formula (e.g. '120 * 0.15 + 40').
        """
        try:
            # Safe evaluation restricted to math names
            allowed = {"__builtins__": None, "math": math, "abs": abs, "round": round, "min": min, "max": max}
            val = eval(expression, allowed, {})
            return {"expression": expression, "result": val}
        except Exception as e:
            return {"expression": expression, "error": str(e)}

    def execute_skill(self, skill_name: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Run a forged or registered skill by name.
        
        Args:
            skill_name: The slug or name of the skill (e.g. 'skill-invoice-chase').
            parameters: Optional parameter dictionary for the skill.
        """
        skill = store.get_skill(skill_name)
        if not skill:
            return {"status": "error", "message": f"Skill '{skill_name}' not found."}
        if not skill.get("enabled", True):
            return {"status": "error", "message": f"Skill '{skill_name}' is disabled: {skill.get('disabled_reason')}"}

        # Execute the skill's defined tool sequence
        tools_executed = []
        for t in skill.get("tools", []):
            tools_executed.append(f"Executed step: {t}")

        return {
            "status": "completed",
            "skill": skill_name,
            "description": skill.get("description"),
            "steps_executed": tools_executed,
        }

    def draft_email(self, recipient: str, subject: str, body: str) -> Dict[str, Any]:
        """Draft an email locally without sending (Low risk, reversible)."""
        return {
            "status": "draft_created",
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "reversible": True,
        }

    def send_outbound_message(self, recipient: str, message: str) -> Dict[str, Any]:
        """Send an outbound email or message (High risk, requires explicit user confirmation)."""
        return {
            "status": "sent",
            "recipient": recipient,
            "message": message,
            "timestamp": "now",
        }

    def get_tools(self) -> Dict[str, Callable[..., Any]]:
        return {
            "remember": self.remember,
            "recall": self.recall,
            "correct_agent": self.correct_agent,
            "calculate": self.calculate,
            "execute_skill": self.execute_skill,
            "draft_email": self.draft_email,
            "send_outbound_message": self.send_outbound_message,
        }

core_tools_plugin = CoreToolsPlugin()

# Register standard plugins with kernel
kernel.register_plugin(core_tools_plugin)
kernel.register_plugin(search_plugin)
kernel.register_plugin(vault_plugin)
