import hashlib
import re
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from app.config import settings
from app.store import store

_STOP_WORDS = {
    "the", "a", "an", "please", "can", "you", "my", "me", "i", "to", "for", "of",
    "and", "is", "it", "this", "that", "in", "on", "at", "with", "from", "by", "about",
    "will", "would", "could", "should", "do", "does", "did", "have", "has", "had",
}

def fingerprint(intent: str, tools_used: List[str]) -> str:
    """Stable deterministic identifier for 'the same kind of task'.
    Executed in pure Python, costing zero tokens.
    """
    words = re.sub(r"[^a-z0-9 ]", " ", intent.lower()).split()
    keywords = sorted(w for w in words if w not in _STOP_WORDS and len(w) > 2)
    normalized_tools = sorted(set(tools_used))
    basis = "|".join(keywords) + "::" + "|".join(normalized_tools)
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]

def record_task_execution(intent: str, tools_used: List[str]) -> str:
    """Records a task completion fingerprint in the durable store."""
    fp = fingerprint(intent, tools_used)
    store.add_fingerprint(fp, intent, tools_used)
    return fp

def count_recent_occurrences(fp: str, days: int = 7) -> int:
    """Counts occurrences of a fingerprint in the rolling N-day window."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    recent = store.get_recent_fingerprints(fp, cutoff)
    return len(recent)

def should_promote(fp: str) -> bool:
    """Pure code threshold evaluation: >= 3 occurrences in 7 days, not already forged."""
    if store.get_skill(fp) is not None:
        # Check if any skill has this fp
        return False
    for s in store.list_skills():
        if s.get("fp") == fp:
            return False
    count = count_recent_occurrences(fp, days=settings.skill_forge_window_days)
    return count >= settings.skill_forge_threshold

def forge_skill(
    intent: str,
    tools_used: List[str],
    fp: Optional[str] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Dict[str, Any]:
    """Creates a forged skill and registers it in the skill registry."""
    if fp is None:
        fp = fingerprint(intent, tools_used)

    if not name:
        # Generate clean slug name from intent keywords
        words = [w for w in re.sub(r"[^a-z0-9 ]", " ", intent.lower()).split() if w not in _STOP_WORDS and len(w) > 2]
        slug = "-".join(words[:3]) if words else "auto-task"
        name = f"skill-{slug}-{fp[:6]}"

    if not description:
        description = f"Automated skill derived from repeated requests: '{intent}'. Executes: {', '.join(tools_used)}."

    skill_data = {
        "name": name,
        "fp": fp,
        "description": description,
        "intent_template": intent,
        "tools": tools_used,
        "version": "1.0.0",
        "enabled": True,
        "provisional": True,
        "invocations": 0,
        "succeeded": 0,
        "corrected": 0,
        "abandoned": 0,
        "success_rate": 1.0,
        "disabled_reason": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_invoked": None,
    }

    store.save_skill(skill_data)
    return skill_data

def record_skill_outcome(name: str, outcome: str) -> Optional[Dict[str, Any]]:
    """Updates skill execution record and performs deterministic auto-retirement.
    Outcome must be one of: 'succeeded', 'corrected', 'abandoned'.
    """
    skill = store.get_skill(name)
    if not skill:
        return None

    skill["invocations"] = skill.get("invocations", 0) + 1
    skill["last_invoked"] = datetime.now(timezone.utc).isoformat()

    if outcome == "succeeded":
        skill["succeeded"] = skill.get("succeeded", 0) + 1
    elif outcome == "corrected":
        skill["corrected"] = skill.get("corrected", 0) + 1
    elif outcome == "abandoned":
        skill["abandoned"] = skill.get("abandoned", 0) + 1

    invocations = skill["invocations"]
    succeeded = skill["succeeded"]
    success_rate = succeeded / invocations if invocations > 0 else 0.0
    skill["success_rate"] = round(success_rate, 2)

    # Bookkeeping: provisional state
    if invocations >= settings.skill_retirement_min_invocations:
        skill["provisional"] = False

        # Auto-retirement check: success rate < 60% over >= 5 invocations
        if success_rate < settings.skill_retirement_min_success_rate:
            skill["enabled"] = False
            skill["disabled_reason"] = (
                f"Auto-disabled: Success rate {int(success_rate * 100)}% ({succeeded}/{invocations}) "
                f"fell below minimum {int(settings.skill_retirement_min_success_rate * 100)}% threshold."
            )

    store.save_skill(skill)
    return skill

def list_skills_command() -> List[Dict[str, Any]]:
    """Returns the formatted listing for `/skill`."""
    skills = store.list_skills()
    result = []
    for s in skills:
        status = "Active" if s.get("enabled", True) else f"Disabled ({s.get('disabled_reason', 'Low success rate')})"
        badge = "[Provisional]" if s.get("provisional", True) else "[Verified]"
        result.append({
            "name": s["name"],
            "badge": badge,
            "status": status,
            "description": s.get("description", ""),
            "tools": s.get("tools", []),
            "invocations": s.get("invocations", 0),
            "success_rate": f"{int(s.get('success_rate', 1.0) * 100)}%",
            "enabled": s.get("enabled", True),
        })
    return result
