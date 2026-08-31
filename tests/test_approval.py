import pytest
from app.approval import ApprovalLayer
from app.plugins.base import ToolEffect

def test_high_risk_always_requires_approval():
    layer = ApprovalLayer(hands_off=False)
    req, reason = layer.check_approval("send_email", ToolEffect(risk="high"))
    assert req is True
    assert "HIGH RISK" in reason

def test_high_risk_cannot_be_silenced_in_hands_off():
    layer = ApprovalLayer(hands_off=True)
    req, reason = layer.check_approval("send_outbound_payment", ToolEffect(risk="high"))
    assert req is True
    assert "HIGH RISK" in reason

def test_medium_risk_auto_approves_in_hands_off():
    normal_layer = ApprovalLayer(hands_off=False)
    req_normal, _ = normal_layer.check_approval("delete_temp_cache", ToolEffect(risk="medium"))
    assert req_normal is True

    hands_off_layer = ApprovalLayer(hands_off=True)
    req_hands_off, _ = hands_off_layer.check_approval("delete_temp_cache", ToolEffect(risk="medium"))
    assert req_hands_off is False

def test_none_risk_silent():
    layer = ApprovalLayer(hands_off=False)
    req, _ = layer.check_approval("calculate", ToolEffect(risk="none"))
    assert req is False
