import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from google.cloud import firestore
from app.config import settings

class DurableStore:
    def __init__(self):
        self._firestore_client = None
        self._use_local = False
        self._local_file = Path("local_store.json")
        self._local_data: Dict[str, Any] = {
            "taste": {},
            "memory": {},
            "corrections": {},
            "skills": {},
            "fingerprints": [],
            "jobs": {},
            "deliveries": {},
            "runs": [],
            "research": {},
        }
        self._init_store()

    def _init_store(self):
        try:
            # Attempt to connect to Google Cloud Firestore if credentials or project are present
            if os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or os.getenv("GOOGLE_CLOUD_PROJECT"):
                self._firestore_client = firestore.Client(project=settings.project_id)
                self._use_local = False
            else:
                self._use_local = True
                self._load_local_data()
        except Exception:
            self._use_local = True
            self._load_local_data()

    def _load_local_data(self):
        if self._local_file.exists():
            try:
                with open(self._local_file, "r") as f:
                    self._local_data = json.load(f)
            except Exception:
                pass

    def _save_local_data(self):
        if self._use_local:
            try:
                with open(self._local_file, "w") as f:
                    json.dump(self._local_data, f, indent=2, default=str)
            except Exception:
                pass

    def is_cloud(self) -> bool:
        return not self._use_local and self._firestore_client is not None

    def get_user_ref(self):
        if self.is_cloud():
            return self._firestore_client.collection("users").document(settings.uid)
        return None

    # Memory Palace Operations
    def add_memory_item(self, room: str, locus: str, item: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        doc_id = f"{room}_{locus}_{len(self._local_data['memory']) + 1}".replace(" ", "_").lower()
        now = datetime.now(timezone.utc).isoformat()
        entry = {
            "id": doc_id,
            "room": room,
            "locus": locus,
            "item": item,
            "decay_score": 1.0,
            "access_count": 1,
            "created_at": now,
            "last_accessed": now,
            "provenance": metadata.get("provenance", "user_direct") if metadata else "user_direct",
            "metadata": metadata or {},
        }

        if self.is_cloud():
            self.get_user_ref().collection("memory").document(doc_id).set(entry)
        else:
            self._local_data["memory"][doc_id] = entry
            self._save_local_data()
        return doc_id

    def list_memory_items(self) -> List[Dict[str, Any]]:
        if self.is_cloud():
            docs = self.get_user_ref().collection("memory").stream()
            return [d.to_dict() for d in docs]
        return list(self._local_data["memory"].values())

    def update_memory_access(self, doc_id: str):
        now = datetime.now(timezone.utc).isoformat()
        if self.is_cloud():
            doc_ref = self.get_user_ref().collection("memory").document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                d = doc.to_dict()
                count = d.get("access_count", 0) + 1
                doc_ref.update({"last_accessed": now, "access_count": count, "decay_score": min(1.0, d.get("decay_score", 1.0) + 0.1)})
        elif doc_id in self._local_data["memory"]:
            self._local_data["memory"][doc_id]["last_accessed"] = now
            self._local_data["memory"][doc_id]["access_count"] += 1
            self._local_data["memory"][doc_id]["decay_score"] = min(1.0, self._local_data["memory"][doc_id]["decay_score"] + 0.1)
            self._save_local_data()

    # Fingerprint Operations for Skill Forge
    def add_fingerprint(self, fp: str, intent: str, tools: List[str]) -> str:
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "fp": fp,
            "intent": intent,
            "tools": tools,
            "ts": now,
        }
        if self.is_cloud():
            self.get_user_ref().collection("fingerprints").add(record)
        else:
            self._local_data["fingerprints"].append(record)
            self._save_local_data()
        return fp

    def get_recent_fingerprints(self, fp: str, cutoff_iso: str) -> List[Dict[str, Any]]:
        if self.is_cloud():
            docs = (
                self.get_user_ref()
                .collection("fingerprints")
                .where("fp", "==", fp)
                .where("ts", ">=", cutoff_iso)
                .stream()
            )
            return [d.to_dict() for d in docs]
        return [
            item for item in self._local_data["fingerprints"]
            if item.get("fp") == fp and item.get("ts", "") >= cutoff_iso
        ]

    # Skill Registry Operations
    def save_skill(self, skill_data: Dict[str, Any]) -> str:
        name = skill_data["name"]
        if self.is_cloud():
            self.get_user_ref().collection("skills").document(name).set(skill_data)
        else:
            self._local_data["skills"][name] = skill_data
            self._save_local_data()
        return name

    def get_skill(self, name: str) -> Optional[Dict[str, Any]]:
        if self.is_cloud():
            doc = self.get_user_ref().collection("skills").document(name).get()
            return doc.to_dict() if doc.exists else None
        return self._local_data["skills"].get(name)

    def list_skills(self) -> List[Dict[str, Any]]:
        if self.is_cloud():
            docs = self.get_user_ref().collection("skills").stream()
            return [d.to_dict() for d in docs]
        return list(self._local_data["skills"].values())

    # Correction Ledger Operations
    def add_correction(self, correction_data: Dict[str, Any]) -> str:
        rule_id = f"rule_{len(self._local_data['corrections']) + 1}"
        correction_data["id"] = rule_id
        correction_data["created_at"] = datetime.now(timezone.utc).isoformat()
        if self.is_cloud():
            self.get_user_ref().collection("corrections").document(rule_id).set(correction_data)
        else:
            self._local_data["corrections"][rule_id] = correction_data
            self._save_local_data()
        return rule_id

    def list_corrections(self, active_only: bool = False) -> List[Dict[str, Any]]:
        if self.is_cloud():
            query = self.get_user_ref().collection("corrections")
            if active_only:
                query = query.where("active", "==", True)
            docs = query.stream()
            return [d.to_dict() for d in docs]
        rules = list(self._local_data["corrections"].values())
        if active_only:
            rules = [r for r in rules if r.get("active", True)]
        return rules

    def update_correction(self, rule_id: str, updates: Dict[str, Any]):
        if self.is_cloud():
            self.get_user_ref().collection("corrections").document(rule_id).update(updates)
        elif rule_id in self._local_data["corrections"]:
            self._local_data["corrections"][rule_id].update(updates)
            self._save_local_data()

    # Research & Morning Reports
    def save_research_report(self, report_data: Dict[str, Any]) -> str:
        report_id = f"report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        report_data["id"] = report_id
        report_data["created_at"] = datetime.now(timezone.utc).isoformat()
        if self.is_cloud():
            self.get_user_ref().collection("research").document(report_id).set(report_data)
        else:
            self._local_data["research"][report_id] = report_data
            self._save_local_data()
        return report_id

    def list_research_reports(self) -> List[Dict[str, Any]]:
        if self.is_cloud():
            docs = self.get_user_ref().collection("research").stream()
            return [d.to_dict() for d in docs]
        return list(self._local_data["research"].values())

    # Taste Model
    def get_taste_profile(self) -> Dict[str, Any]:
        default_taste = {
            "verbosity": 0.4,       # 0.0 (very concise) to 1.0 (detailed)
            "formality": 0.3,       # 0.0 (casual) to 1.0 (formal)
            "directness": 0.9,      # 0.0 (diplomatic) to 1.0 (blunt/direct)
            "format_preference": "markdown_structured",
            "risk_tolerance": "moderate",
            "accepted_count": 0,
            "rejected_count": 0,
        }
        if self.is_cloud():
            doc = self.get_user_ref().collection("taste").document("profile").get()
            return doc.to_dict() if doc.exists else default_taste
        return self._local_data.get("taste", {}).get("profile", default_taste)

    def update_taste_profile(self, updates: Dict[str, Any]):
        current = self.get_taste_profile()
        current.update(updates)
        if self.is_cloud():
            self.get_user_ref().collection("taste").document("profile").set(current)
        else:
            if "taste" not in self._local_data:
                self._local_data["taste"] = {}
            self._local_data["taste"]["profile"] = current
            self._save_local_data()

    def reset_for_benchmark(self):
        """Clears memory, forged skills, and corrections for cold benchmark testing."""
        self._local_data["memory"] = {}
        self._local_data["skills"] = {}
        self._local_data["corrections"] = {}
        self._local_data["fingerprints"] = []
        self._save_local_data()

store = DurableStore()
