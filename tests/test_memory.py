import pytest
from app.memory import palace
from app.store import store

def test_memory_palace_spatial_classification():
    room, locus = palace.determine_room_and_locus("Project Alpha architecture decisions")
    assert room == "projects"
    assert locus == "architecture"

def test_memory_store_and_retrieve_hierarchy():
    store.reset_for_benchmark()
    palace.store_memory(
        "User prefers concise plain text bullet points.",
        room="preferences",
        locus="formatting",
        provenance="user_direct",
    )
    
    results = palace.retrieve("preferred formatting style", room="preferences")
    assert len(results) > 0
    assert "concise" in results[0]["item"]
    assert results[0]["room"] == "preferences"
    assert results[0]["provenance"] == "user_direct"

def test_memory_tree_structure():
    store.reset_for_benchmark()
    palace.store_memory("Test project item", room="projects", locus="kiw1")
    tree = palace.get_palace_tree()
    assert "Projects" in tree
    assert "Kiw1" in tree["Projects"]
    assert len(tree["Projects"]["Kiw1"]) >= 1
