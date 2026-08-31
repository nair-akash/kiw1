import re
from typing import Any, Dict, List, Optional
from app.store import store

class CorrectionLedger:
    """The self-learning feedback loop.
    Turns user corrections into durable rules retrieved before future actions.
    Reinforcement and retirement are deterministic bookkeeping.
    """

    def record_correction(
        self,
        situation: str,
        wrong_action: str,
        correction: str,
        rule: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Records a correction and generates a durable rule."""
        if not rule:
            rule = f"When {situation.strip()}, avoid '{wrong_action.strip()}' and instead {correction.strip()}."

        correction_data = {
            "situation": situation,
            "wrong_action": wrong_action,
            "correction": correction,
            "rule": rule,
            "weight": 1.0,
            "reinforcement_count": 0,
            "contradiction_count": 0,
            "active": True,
            "retired_reason": None,
        }
        rule_id = store.add_correction(correction_data)
        correction_data["id"] = rule_id
        return correction_data

    def find_relevant_rules(self, context_text: str, threshold: float = 0.2) -> List[Dict[str, Any]]:
        """Retrieves active rules relevant to the current task context before execution."""
        active_rules = store.list_corrections(active_only=True)
        if not active_rules:
            return []

        context_words = set(re.findall(r"\b[a-z0-9_-]+\b", context_text.lower()))
        matched_rules = []

        def _stem(w: str) -> str:
            # Simple fast pure-python suffix stripping for matching
            for suffix in ["ing", "tion", "ed", "es", "s", "ly"]:
                if w.endswith(suffix) and len(w) > len(suffix) + 2:
                    return w[:-len(suffix)]
            return w

        context_stems = {_stem(w) for w in context_words if len(w) > 2}

        for r in active_rules:
            # Score against situation, wrong action, and rule text
            target_text = (r.get("situation", "") + " " + r.get("rule", "")).lower()
            target_words = set(re.findall(r"\b[a-z0-9_-]+\b", target_text))
            target_stems = {_stem(w) for w in target_words if len(w) > 2}

            overlap = len(context_words.intersection(target_words))
            stem_overlap = len(context_stems.intersection(target_stems))
            total_matches = max(overlap, stem_overlap)

            # Score prioritizes absolute match count and percentage of context matched
            match_ratio = (total_matches / len(context_stems)) if context_stems else 0.0
            score = (total_matches * 1.5 + match_ratio) * r.get("weight", 1.0)

            if total_matches >= 1:
                matched_rules.append((score, r))

        matched_rules.sort(key=lambda x: x[0], reverse=True)
        return [r for _, r in matched_rules]

    def reinforce_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Increases weight of a rule that successfully prevented a mistake."""
        rules = store.list_corrections()
        target = next((r for r in rules if r.get("id") == rule_id), None)
        if not target:
            return None

        new_weight = min(2.0, target.get("weight", 1.0) + 0.2)
        count = target.get("reinforcement_count", 0) + 1
        store.update_correction(rule_id, {"weight": round(new_weight, 2), "reinforcement_count": count})
        target["weight"] = round(new_weight, 2)
        target["reinforcement_count"] = count
        return target

    def record_contradiction(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """Increments contradiction count. Retires rule if contradicted twice."""
        rules = store.list_corrections()
        target = next((r for r in rules if r.get("id") == rule_id), None)
        if not target:
            return None

        contradictions = target.get("contradiction_count", 0) + 1
        updates: Dict[str, Any] = {"contradiction_count": contradictions}

        if contradictions >= 2:
            updates["active"] = False
            updates["retired_reason"] = "Auto-retired: Rule contradicted twice in subsequent user corrections."

        store.update_correction(rule_id, updates)
        target.update(updates)
        return target

    def list_rules(self) -> List[Dict[str, Any]]:
        """Lists all rules in the correction ledger."""
        return store.list_corrections()

ledger = CorrectionLedger()
