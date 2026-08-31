import pytest
from app.refinery import refinery

def test_refinery_detects_ambiguous_short_prompt():
    is_ambiguous, reasons = refinery.classify_ambiguity("Fix it")
    assert is_ambiguous is True
    assert len(reasons) > 0

def test_refinery_detects_unresolved_pronouns():
    is_ambiguous, reasons = refinery.classify_ambiguity("Send that to them now")
    assert is_ambiguous is True

def test_refinery_passes_clear_prompt():
    is_ambiguous, reasons = refinery.classify_ambiguity(
        "Remember that the default timeout for database connections is 30 seconds."
    )
    assert is_ambiguous is False
    assert len(reasons) == 0

def test_refinery_generates_max_3_questions():
    brief = refinery.refine("Make it better")
    assert brief.is_ambiguous is True
    assert 1 <= len(brief.questions) <= 3
    for q in brief.questions:
        assert len(q.options) >= 2
