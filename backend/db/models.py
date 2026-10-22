import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON
from .database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    language = Column(String, default="en")
    daily_refund_total = Column(Integer, default=0)
    trust_score = Column(Float, default=0.95)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False)
    merchant_id = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, default="DELIVERED") # DELIVERED, SHIPPED, CANCELLED, REFUNDED
    refund_status = Column(String, default="NONE") # NONE, REFUNDED, REFUND_PENDING
    delivery_status = Column(String, default="DELIVERED_SIGNED") # DELIVERED_SIGNED, IN_TRANSIT, FAILED
    placed_at = Column(DateTime, default=datetime.datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)

class Payment(Base):
    __tablename__ = "payments"

    upi_ref = Column(String, primary_key=True)
    customer_id = Column(String, nullable=False)
    order_id = Column(String, nullable=True)
    amount = Column(Integer, nullable=False)
    bank = Column(String, default="HDFC")
    status = Column(String, default="SUCCESS") # SUCCESS, FAILED_DEBITED, PENDING, REVERSED
    debited_at = Column(DateTime, default=datetime.datetime.utcnow)
    expected_reversal_at = Column(DateTime, nullable=True)

class Refund(Base):
    __tablename__ = "refunds"

    id = Column(String, primary_key=True)
    order_id = Column(String, nullable=False)
    customer_id = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, default="COMPLETED") # COMPLETED, UNDONE, PENDING_APPROVAL
    reason = Column(String, nullable=False)
    rule_ids = Column(String, nullable=True)
    undo_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    undone_at = Column(DateTime, nullable=True)
    undone_by = Column(String, nullable=True)

class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    vpa = Column(String, nullable=False)
    category = Column(String, default="Retail")
    dispute_rate = Column(Float, default=0.012)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Settlement(Base):
    __tablename__ = "settlements"

    id = Column(String, primary_key=True)
    merchant_id = Column(String, nullable=False)
    date = Column(String, nullable=False)
    gross_amount = Column(Integer, nullable=False)
    fee = Column(Integer, nullable=False)
    net_amount = Column(Integer, nullable=False)
    status = Column(String, default="SETTLED") # SETTLED, DISPUTED, ON_HOLD
    dispute_reason = Column(String, nullable=True)

class AuditEntry(Base):
    __tablename__ = "audit_entries"

    id = Column(String, primary_key=True)
    seq = Column(Integer, nullable=False, unique=True)
    session_id = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)
    actor = Column(String, nullable=False) # AGENT, SUPERVISOR, POLICY_ENGINE, SYSTEM
    action = Column(String, nullable=False)
    inputs = Column(JSON, nullable=False)
    result = Column(JSON, nullable=False)
    rule_ids = Column(String, nullable=True)
    confidence = Column(Float, default=1.0)
    reasoning = Column(Text, nullable=False)
    prev_hash = Column(String, nullable=False)
    hash = Column(String, nullable=False)

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False)
    customer_id = Column(String, nullable=False)
    action_type = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED, TAKEN_OVER
    packet = Column(JSON, nullable=False) # {issue, steps_taken, evidence, sentiment, suggested_step}
    decided_by = Column(String, nullable=True)
    decided_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class HistoricalCase(Base):
    __tablename__ = "historical_cases"

    id = Column(String, primary_key=True)
    case_name = Column(String, nullable=False)
    customer_id = Column(String, nullable=False)
    order_id = Column(String, nullable=True)
    amount = Column(Integer, nullable=False)
    proposed_action = Column(String, nullable=False)
    action_args = Column(JSON, nullable=False)
    context_data = Column(JSON, nullable=False)
    original_verdict = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
