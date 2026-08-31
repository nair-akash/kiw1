import os
import re
from pathlib import Path
from typing import Any, Callable, Dict, List
from app.boundary import vault_boundary
from app.config import settings
from app.plugins.base import BasePlugin, PluginManifest, ToolEffect

class LocalVaultPlugin(BasePlugin):
    """Local Vault Node Plugin adhering to the Local Data Boundary (PRD §3.1).
    Local files are processed on-device; only local answer summaries cross the boundary.
    """

    def __init__(self):
        manifest = PluginManifest(
            name="vault_node",
            version="1.0.0",
            requires=[],
            provides_tools=["query_vault"],
            effects={
                "query_vault": ToolEffect(reversible=True, risk="none", approval="never"),
            },
            capabilities=["filesystem:local_vault"],
            cost_class="cheap",
            description="Local Vault search maintaining local data privacy (answers-only egress)",
        )
        super().__init__(manifest)
        self.vault_dir = Path(settings.local_vault_path)

    def _local_search(self, question: str) -> str:
        """Searches local markdown files in seed/synthetic_vault and synthesizes an answer locally."""
        if not self.vault_dir.exists():
            return f"No local notes found at {self.vault_dir}."

        words = set(re.findall(r"\b[a-z0-9_-]+\b", question.lower()))
        matched_notes = []

        for md_file in self.vault_dir.glob("**/*.md"):
            try:
                with open(md_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    file_words = set(re.findall(r"\b[a-z0-9_-]+\b", content.lower()))
                    overlap = len(words.intersection(file_words))
                    if overlap > 0:
                        # Extract matching key sentences locally
                        lines = [line.strip() for line in content.splitlines() if line.strip()]
                        summary_lines = [l for l in lines if any(w in l.lower() for w in words)][:3]
                        matched_notes.append({
                            "title": md_file.stem,
                            "summary": " ".join(summary_lines),
                            "score": overlap,
                        })
            except Exception:
                pass

        if not matched_notes:
            return f"Local vault searched ({len(list(self.vault_dir.glob('**/*.md')))} notes indexed). No matching notes for: '{question}'."

        matched_notes.sort(key=lambda x: x["score"], reverse=True)
        top = matched_notes[0]
        return f"[Local Vault Synthesis] Found relevant note '{top['title']}': {top['summary']}"

    def query_vault(self, question: str) -> Dict[str, Any]:
        """Queries local notes via the privacy boundary."""
        return vault_boundary.process_vault_query(question, self._local_search)

    def get_tools(self) -> Dict[str, Callable[..., Any]]:
        return {
            "query_vault": self.query_vault,
        }

vault_plugin = LocalVaultPlugin()
