import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..db.database import SessionLocal
from ..db.models import Customer, Order, Payment, Refund, Settlement, Merchant

# Failure injection states for testing/demo (Feature 16)
class FailureInjection:
    def __init__(self):
        self.refund_timeout = False
        self.crm_down = False
        self.db_error = False

    def toggle(self, key: str, value: bool):
        if hasattr(self, key):
            setattr(self, key, value)

    def get_status(self) -> Dict[str, bool]:
        return {
            "refund_timeout": self.refund_timeout,
            "crm_down": self.crm_down,
            "db_error": self.db_error
        }

failure_flags = FailureInjection()

class MockPaytmServices:
    @staticmethod
    def get_order(order_id: str) -> Dict[str, Any]:
        if failure_flags.db_error:
            raise RuntimeError("Database connection pool timeout (Simulated Failure)")

        db: Session = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return {"found": False, "error": f"Order {order_id} not found."}

            age_days = (datetime.datetime.now(datetime.timezone.utc) - order.placed_at.replace(tzinfo=datetime.timezone.utc)).days
            return {
                "found": True,
                "order_id": order.id,
                "customer_id": order.customer_id,
                "merchant_id": order.merchant_id,
                "item_name": order.item_name,
                "amount": order.amount,
                "status": order.status,
                "refund_status": order.refund_status,
                "delivery_status": order.delivery_status,
                "placed_at": order.placed_at.isoformat(),
                "delivered_at": order.delivered_at.isoformat() if order.delivered_at else None,
                "order_age_days": age_days
            }
        finally:
            db.close()

    @staticmethod
    def get_payment(upi_ref: str) -> Dict[str, Any]:
        if failure_flags.db_error:
            raise RuntimeError("Database connection pool timeout (Simulated Failure)")

        db: Session = SessionLocal()
        try:
            payment = db.query(Payment).filter(Payment.upi_ref == upi_ref).first()
            if not payment:
                return {"found": False, "error": f"Payment {upi_ref} not found."}

            elapsed_hours = int((datetime.datetime.now(datetime.timezone.utc) - payment.debited_at.replace(tzinfo=datetime.timezone.utc)).total_seconds() / 3600)
            return {
                "found": True,
                "upi_ref": payment.upi_ref,
                "customer_id": payment.customer_id,
                "order_id": payment.order_id,
                "amount": payment.amount,
                "bank": payment.bank,
                "status": payment.status,
                "debited_at": payment.debited_at.isoformat(),
                "elapsed_hours": elapsed_hours,
                "expected_reversal_at": payment.expected_reversal_at.isoformat() if payment.expected_reversal_at else None
            }
        finally:
            db.close()

    @staticmethod
    def get_customer_history(customer_id: str) -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            cust = db.query(Customer).filter(Customer.id == customer_id).first()
            if not cust:
                return {"found": False, "error": f"Customer {customer_id} not found."}

            recent_orders = db.query(Order).filter(Order.customer_id == customer_id).limit(5).all()
            return {
                "found": True,
                "customer_id": cust.id,
                "name": cust.name,
                "phone": cust.phone,
                "language": cust.language,
                "daily_refund_total": cust.daily_refund_total,
                "trust_score": cust.trust_score,
                "recent_orders": [
                    {
                        "id": o.id,
                        "item": o.item_name,
                        "amount": o.amount,
                        "status": o.status,
                        "refund_status": o.refund_status
                    }
                    for o in recent_orders
                ]
            }
        finally:
            db.close()

    @staticmethod
    def issue_refund(order_id: str, amount: int, reason: str, rule_ids: str = "") -> Dict[str, Any]:
        if failure_flags.refund_timeout:
            raise TimeoutError("Bank Gateway 504 Gateway Timeout while processing refund (Simulated Failure)")

        db: Session = SessionLocal()
        try:
            order = db.query(Order).filter(Order.id == order_id).first()
            if not order:
                return {"success": False, "error": f"Order {order_id} not found."}

            if order.refund_status == "REFUNDED":
                return {"success": False, "error": "Order already marked as refunded."}

            cust = db.query(Customer).filter(Customer.id == order.customer_id).first()

            refund_id = f"REF-{int(datetime.datetime.now().timestamp() * 1000) % 1000000}"
            now = datetime.datetime.now(datetime.timezone.utc)
            undo_until = now + datetime.timedelta(minutes=10)

            refund = Refund(
                id=refund_id,
                order_id=order.id,
                customer_id=order.customer_id,
                amount=amount,
                status="COMPLETED",
                reason=reason,
                rule_ids=rule_ids,
                undo_until=undo_until,
                created_at=now
            )
            order.status = "REFUNDED"
            order.refund_status = "REFUNDED"

            if cust:
                cust.daily_refund_total += amount

            db.add(refund)
            db.commit()

            return {
                "success": True,
                "refund_id": refund.id,
                "order_id": order.id,
                "amount": amount,
                "status": "COMPLETED",
                "undo_until": undo_until.isoformat(),
                "undo_window_minutes": 10,
                "message": f"₹{amount} refunded successfully to customer account."
            }
        finally:
            db.close()

    @staticmethod
    def undo_refund(refund_id: str, reason: str, supervisor_id: str = "SUPERVISOR-ANJALI") -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            refund = db.query(Refund).filter(Refund.id == refund_id).first()
            if not refund:
                return {"success": False, "error": f"Refund record {refund_id} not found."}

            if refund.status != "COMPLETED":
                return {"success": False, "error": f"Refund is already in '{refund.status}' state."}

            now = datetime.datetime.now(datetime.timezone.utc)
            if refund.undo_until and now > refund.undo_until.replace(tzinfo=datetime.timezone.utc):
                return {"success": False, "error": "Undo window (10 minutes) has expired. Standard reversal escalation required."}

            refund.status = "UNDONE"
            refund.undone_at = now
            refund.undone_by = supervisor_id

            order = db.query(Order).filter(Order.id == refund.order_id).first()
            if order:
                order.status = "DELIVERED"
                order.refund_status = "NONE"

            cust = db.query(Customer).filter(Customer.id == refund.customer_id).first()
            if cust:
                cust.daily_refund_total = max(0, cust.daily_refund_total - refund.amount)

            db.commit()

            return {
                "success": True,
                "refund_id": refund.id,
                "status": "UNDONE",
                "reversed_amount": refund.amount,
                "undone_by": supervisor_id,
                "message": f"Refund {refund_id} for ₹{refund.amount} successfully undone."
            }
        finally:
            db.close()

    @staticmethod
    def request_upi_reversal(upi_ref: str, amount: int, reason: str = "") -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            payment = db.query(Payment).filter(Payment.upi_ref == upi_ref).first()
            if not payment:
                return {"success": False, "error": f"Payment {upi_ref} not found."}

            ticket_ref = f"TKT-UPI-{int(datetime.datetime.now().timestamp()) % 100000}"
            now = datetime.datetime.now(datetime.timezone.utc)
            expected_reversal = now + datetime.timedelta(hours=24)
            payment.expected_reversal_at = expected_reversal

            db.commit()

            return {
                "success": True,
                "ticket_ref": ticket_ref,
                "upi_ref": upi_ref,
                "amount": amount,
                "status": "REVERSAL_REQUESTED",
                "bank": payment.bank,
                "expected_reversal_at": expected_reversal.isoformat(),
                "message": f"Reversal ticket {ticket_ref} submitted to {payment.bank} clearing house."
            }
        finally:
            db.close()

    @staticmethod
    def update_crm(customer_id: str, issue_summary: str, resolution_notes: str) -> Dict[str, Any]:
        if failure_flags.crm_down:
            raise RuntimeError("CRM Gateway 503 Service Unavailable (Simulated Failure)")

        ticket_id = f"CRM-{int(datetime.datetime.now().timestamp()) % 100000}"
        return {
            "success": True,
            "ticket_id": ticket_id,
            "customer_id": customer_id,
            "status": "RESOLVED",
            "summary": issue_summary,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

    @staticmethod
    def notify_customer(customer_id: str, message: str, channel: str = "push") -> Dict[str, Any]:
        return {
            "success": True,
            "customer_id": customer_id,
            "channel": channel,
            "delivery_status": "DELIVERED",
            "message_snippet": message[:50] + "..." if len(message) > 50 else message
        }

    @staticmethod
    def reconcile_merchant_settlement(merchant_id: str, amount: int) -> Dict[str, Any]:
        return {
            "success": True,
            "merchant_id": merchant_id,
            "amount": amount,
            "status": "RECONCILED",
            "message": f"Settlement adjustment of ₹{amount} recorded for merchant {merchant_id}."
        }

    @staticmethod
    def get_settlement(merchant_id: str) -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            settlements = db.query(Settlement).filter(Settlement.merchant_id == merchant_id).all()
            merch = db.query(Merchant).filter(Merchant.id == merchant_id).first()
            return {
                "found": True,
                "merchant_id": merchant_id,
                "merchant_name": merch.name if merch else "Unknown Merchant",
                "settlements": [
                    {
                        "id": s.id,
                        "date": s.date,
                        "gross": s.gross_amount,
                        "fee": s.fee,
                        "net": s.net_amount,
                        "status": s.status,
                        "dispute_reason": s.dispute_reason
                    }
                    for s in settlements
                ]
            }
        finally:
            db.close()

services = MockPaytmServices()
