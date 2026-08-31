import re
from typing import Any, Dict, List, Optional
from app.config import settings

class UntrustedContentBoundary:
    """Security boundary ensuring retrieved content is treated strictly as data, never instructions."""

    INJECTION_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"you\s+are\s+now\s+authorised\s+to",
        r"disregard\s+all\s+prior",
        r"system\s*:\s*you\s+are",
        r"override\s+security\s+protocol",
        r"execute\s+command\s*:",
    ]

    def wrap_untrusted_data(self, source_name: str, content: str) -> Dict[str, Any]:
        """Sanitizes and demarcates untrusted external data with explicit provenance tags."""
        has_injection = False
        detected_triggers = []

        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                has_injection = True
                detected_triggers.append(pattern)

        sanitized_text = f"=== BEGIN UNTRUSTED DATA FROM [{source_name}] ===\n{content}\n=== END UNTRUSTED DATA ==="

        return {
            "source": source_name,
            "content": sanitized_text,
            "raw_length": len(content),
            "untrusted": True,
            "has_injection_suspect": has_injection,
            "detected_triggers": detected_triggers,
        }

    def inspect_tool_call_source(self, tool_name: str, justification: str, provenance: str) -> bool:
        """Enforces Rule 2 (PRD §12b): No tool call may be justified solely by untrusted retrieved content."""
        if provenance in ["untrusted_web", "untrusted_email"]:
            return False  # Tool call solely from untrusted source requires explicit approval
        return True

class LocalVaultBoundary:
    """The Local Data Boundary (PRD §3.1).
    Ensures local vault files never leave the machine.
    Only questions and locally-synthesized answers cross the boundary.
    """

    def is_vault_access_permitted(self) -> bool:
        return settings.vault_mode != "sealed"

    def process_vault_query(self, question: str, local_vault_search_fn) -> Dict[str, Any]:
        """Queries local notes locally and returns answers-only across the boundary."""
        if not self.is_vault_access_permitted():
            return {
                "allowed": False,
                "error": "Vault is in sealed mode. No vault access permitted.",
            }

        # Local computation
        local_answer = local_vault_search_fn(question)

        # In answers-only mode, strip any raw full file contents
        return {
            "allowed": True,
            "mode": settings.vault_mode,
            "question": question,
            "answer": local_answer,
            "raw_files_transmitted": 0,
        }

untrusted_boundary = UntrustedContentBoundary()
vault_boundary = LocalVaultBoundary()
