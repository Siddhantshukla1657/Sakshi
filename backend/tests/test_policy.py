import pytest
from backend.policy.engine import PolicyEngine
from backend.audit.logger import AuditLogger
from backend.tools.services import MockPaytmServices
from backend.db.seed import seed_database

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

def test_tier_boundaries():
    engine = PolicyEngine()
    context = {"customer_daily_total": 0, "order_age_days": 2, "target_status": "NONE"}

    # Under ₹500 (e.g. ₹499) -> ALLOW
    v_499 = engine.evaluate("issue_refund", {"order_id": "ORD-901", "amount": 499}, context)
    assert v_499.verdict == "ALLOW"
    assert "R-TIER-01" in v_499.rule_ids

    # Exact boundary ₹500 -> NEEDS_APPROVAL
    v_500 = engine.evaluate("issue_refund", {"order_id": "ORD-901", "amount": 500}, context)
    assert v_500.verdict == "NEEDS_APPROVAL"
    assert "R-TIER-02" in v_500.rule_ids

    # ₹5,000 exact -> NEEDS_APPROVAL
    v_5000 = engine.evaluate("issue_refund", {"order_id": "ORD-901", "amount": 5000}, context)
    assert v_5000.verdict == "NEEDS_APPROVAL"
    assert "R-TIER-02" in v_5000.rule_ids

    # ₹5,001 -> ESCALATE (Tier 3)
    v_5001 = engine.evaluate("issue_refund", {"order_id": "ORD-901", "amount": 5001}, context)
    assert v_5001.verdict == "ESCALATE"
    assert "R-TIER-03" in v_5001.rule_ids

def test_duplicate_refund_blocked():
    engine = PolicyEngine()
    context = {"target_status": "REFUNDED", "order_age_days": 2}
    v = engine.evaluate("issue_refund", {"order_id": "ORD-906", "amount": 299}, context)
    assert v.verdict == "DENY"
    assert "R-DUP-01" in v.rule_ids

def test_ownership_mismatch_blocked():
    engine = PolicyEngine()
    context = {"target_customer_id": "CUST-999", "session_customer_id": "CUST-101"}
    v = engine.evaluate("issue_refund", {"order_id": "ORD-901", "amount": 499}, context)
    assert v.verdict == "DENY"
    assert "R-OWN-01" in v.rule_ids

def test_audit_hash_chain_and_tamper():
    # Verify fresh chain
    res = AuditLogger.verify_chain()
    assert res["valid"] is True

    # Append new entry
    new_entry = AuditLogger.append(
        session_id="test-session",
        actor="AGENT",
        action="test_action",
        inputs={"foo": "bar"},
        result={"status": "OK"},
        rule_ids="TEST-01",
        confidence=0.95,
        reasoning="Testing chain"
    )
    assert new_entry["seq"] >= 1

    # Verify again
    res2 = AuditLogger.verify_chain()
    assert res2["valid"] is True

    # Tamper the entry
    AuditLogger.simulate_tamper(new_entry["seq"])
    res_tampered = AuditLogger.verify_chain()
    assert res_tampered["valid"] is False
    assert res_tampered["broken_at_seq"] == new_entry["seq"]
