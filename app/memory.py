import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from app.store import store

class MemoryPalace:
    """Hardcoded spatial memory hierarchy: room -> locus -> item.
    Enforces deterministic spatial indexing before falling back to search.
    """

    KNOWN_ROOMS = {
        "projects": ["kiw1", "agent", "cloud", "code", "architecture", "hackathon"],
        "preferences": ["style", "formatting", "budget", "effort", "tone", "privacy"],
        "system": ["credentials", "endpoints", "models", "limits", "infrastructure"],
        "knowledge": ["research", "findings", "domain", "facts", "notes"],
    }

    def determine_room_and_locus(self, text: str, hint_room: Optional[str] = None, hint_locus: Optional[str] = None) -> tuple[str, str]:
        """Classifies text into room and locus using deterministic keyword mapping in code."""
        if hint_room and hint_locus:
            return hint_room.lower(), hint_locus.lower()

        lower = text.lower()
        matched_room = "knowledge"
        matched_locus = "general"

        for room, keywords in self.KNOWN_ROOMS.items():
            for kw in keywords:
                if kw in lower:
                    matched_room = room
                    matched_locus = kw
                    break

        if hint_room:
            matched_room = hint_room.lower()
        if hint_locus:
            matched_locus = hint_locus.lower()

        return matched_room, matched_locus

    def store_memory(
        self,
        item: str,
        room: Optional[str] = None,
        locus: Optional[str] = None,
        provenance: str = "user_direct",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Stores an item in the Memory Palace with provenance."""
        r, l = self.determine_room_and_locus(item, hint_room=room, hint_locus=locus)
        meta = metadata or {}
        meta["provenance"] = provenance

        doc_id = store.add_memory_item(r, l, item, metadata=meta)
        return {
            "id": doc_id,
            "room": r,
            "locus": l,
            "item": item,
            "provenance": provenance,
            "status": "stored",
        }

    def retrieve(self, query: str, room: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves memories by walking room -> locus first, then keyword relevance."""
        all_items = store.list_memory_items()
        query_words = set(re.findall(r"\b[a-z0-9_-]+\b", query.lower()))

        scored_items = []
        for item in all_items:
            score = 0.0
            item_room = item.get("room", "").lower()
            item_locus = item.get("locus", "").lower()
            item_text = item.get("item", "").lower()
            decay = item.get("decay_score", 1.0)

            # 1. Exact Room Match bonus
            if room and item_room == room.lower():
                score += 3.0

            # 2. Spatial Locus match
            if item_locus in query_words:
                score += 2.0

            # 3. Keyword overlap
            text_words = set(re.findall(r"\b[a-z0-9_-]+\b", item_text))
            overlap = len(query_words.intersection(text_words))
            score += overlap * 1.5

            # Apply decay factor
            final_score = score * decay
            if final_score > 0:
                scored_items.append((final_score, item))

        scored_items.sort(key=lambda x: x[0], reverse=True)
        results = []
        for s, itm in scored_items[:limit]:
            store.update_memory_access(itm["id"])
            results.append({
                "room": itm.get("room"),
                "locus": itm.get("locus"),
                "item": itm.get("item"),
                "score": round(s, 2),
                "provenance": itm.get("provenance", "unknown"),
                "created_at": itm.get("created_at"),
            })
        return results

    def get_palace_tree(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Returns the structured spatial room -> locus -> items tree for visual UI representation."""
        all_items = store.list_memory_items()
        tree: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

        for item in all_items:
            r = item.get("room", "other").capitalize()
            l = item.get("locus", "general").capitalize()
            if r not in tree:
                tree[r] = {}
            if l not in tree[r]:
                tree[r][l] = []
            tree[r][l].append({
                "id": item.get("id"),
                "item": item.get("item"),
                "decay_score": item.get("decay_score", 1.0),
                "access_count": item.get("access_count", 1),
                "provenance": item.get("provenance", "user_direct"),
                "last_accessed": item.get("last_accessed"),
            })
        return tree

palace = MemoryPalace()
