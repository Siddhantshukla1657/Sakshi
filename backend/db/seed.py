import datetime
import hashlib
import json
from .database import engine, Base, SessionLocal
from .models import Customer, Order, Payment, Refund, Merchant, Settlement, AuditEntry, Approval, HistoricalCase

def seed_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Delete rows cleanly without dropping tables to preserve concurrent connections
        db.query(Approval).delete()
        db.query(AuditEntry).delete()
        db.query(Refund).delete()
        db.query(Payment).delete()
        db.query(Order).delete()
        db.query(Settlement).delete()
        db.query(Merchant).delete()
        db.query(Customer).delete()
        db.query(HistoricalCase).delete()
        db.commit()

        now = datetime.datetime.now(datetime.timezone.utc)

        # Seed Customers
        customers = [
            Customer(
                id="CUST-101",
                name="Riya Sharma",
                phone="+91 98765 43210",
                language="hinglish",
                daily_refund_total=0,
                trust_score=0.98
            ),
            Customer(
                id="CUST-102",
                name="Amit Verma",
                phone="+91 98111 22334",
                language="en",
                daily_refund_total=800, # Near ₹1000 daily limit
                trust_score=0.88
            ),
            Customer(
                id="CUST-103",
                name="Mr. Rajesh Patel",
                phone="+91 99200 11223",
                language="en",
                daily_refund_total=0,
                trust_score=0.99
            ),
            Customer(
                id="CUST-104",
                name="Vikram Singh",
                phone="+91 97654 32109",
                language="en",
                daily_refund_total=0,
                trust_score=0.65
            )
        ]
        db.add_all(customers)

        # Seed Merchants
        merchants = [
            Merchant(
                id="MERCH-501",
                name="Patel Kirana & Sweets",
                vpa="patelkirana@paytm",
                category="Retail Grocery",
                dispute_rate=0.012
            ),
            Merchant(
                id="MERCH-502",
                name="Urban Trend Fashion",
                vpa="urbantrend@paytm",
                category="Apparel",
                dispute_rate=0.035
            ),
            Merchant(
                id="MERCH-503",
                name="QuickBite Foods",
                vpa="quickbite@paytm",
                category="Food Delivery",
                dispute_rate=0.018
            )
        ]
        db.add_all(merchants)

        # Seed Orders
        orders = [
            # Happy path: ₹499 Tote Bag, delivered 3 days ago, refund_status NONE
            Order(
                id="ORD-901",
                customer_id="CUST-101",
                merchant_id="MERCH-502",
                item_name="Eco Canvas Tote Bag",
                amount=499,
                status="DELIVERED",
                refund_status="NONE",
                delivery_status="DELIVERED_SIGNED",
                placed_at=now - datetime.timedelta(days=3),
                delivered_at=now - datetime.timedelta(days=2)
            ),
            # Tier 2 approval: ₹1,499 Wireless Earbuds
            Order(
                id="ORD-902",
                customer_id="CUST-101",
                merchant_id="MERCH-502",
                item_name="BassPods Wireless Earbuds",
                amount=1499,
                status="DELIVERED",
                refund_status="NONE",
                delivery_status="DELIVERED_SIGNED",
                placed_at=now - datetime.timedelta(days=2),
                delivered_at=now - datetime.timedelta(days=1)
            ),
            # Tier 3 mandatory human escalate: ₹6,499 Tablet Display
            Order(
                id="ORD-903",
                customer_id="CUST-101",
                merchant_id="MERCH-502",
                item_name="UltraTab 11-inch Display",
                amount=6499,
                status="DELIVERED",
                refund_status="NONE",
                delivery_status="DELIVERED_SIGNED",
                placed_at=now - datetime.timedelta(days=1),
                delivered_at=now - datetime.timedelta(hours=18)
            ),
            # Velocity / Daily Cap test: Amit Verma has ₹800 refunded, requesting ₹450 -> 800+450=1250 > 1000
            Order(
                id="ORD-904",
                customer_id="CUST-102",
                merchant_id="MERCH-501",
                item_name="Artisanal Snack Hamper",
                amount=450,
                status="DELIVERED",
                refund_status="NONE",
                delivery_status="DELIVERED_SIGNED",
                placed_at=now - datetime.timedelta(days=1),
                delivered_at=now - datetime.timedelta(hours=12)
            ),
            # Claim Mismatch: Claims item never delivered, but logistics has signed proof of delivery
            Order(
                id="ORD-905",
                customer_id="CUST-104",
                merchant_id="MERCH-502",
                item_name="Graphic Print Cotton Tee",
                amount=350,
                status="DELIVERED",
                refund_status="NONE",
                delivery_status="DELIVERED_SIGNED", # Verified courier signature on file
                placed_at=now - datetime.timedelta(days=2),
                delivered_at=now - datetime.timedelta(days=1)
            ),
            # Duplicate check: Already refunded
            Order(
                id="ORD-906",
                customer_id="CUST-101",
                merchant_id="MERCH-503",
                item_name="Gourmet Burger Combo",
                amount=299,
                status="REFUNDED",
                refund_status="REFUNDED",
                delivery_status="DELIVERED_SIGNED",
                placed_at=now - datetime.timedelta(days=4),
                delivered_at=now - datetime.timedelta(days=4)
            ),
            # Expired window (>7 days)
            Order(
                id="ORD-907",
                customer_id="CUST-101",
                merchant_id="MERCH-502",
                item_name="Designer Sunglasses",
                amount=480,
                status="DELIVERED",
                refund_status="NONE",
                delivery_status="DELIVERED_SIGNED",
                placed_at=now - datetime.timedelta(days=15),
                delivered_at=now - datetime.timedelta(days=14)
            )
        ]
        db.add_all(orders)

        # Seed Payments
        payments = [
            # Debited but failed within 48h
            Payment(
                upi_ref="UPI-849102",
                customer_id="CUST-101",
                order_id="ORD-901",
                amount=499,
                bank="HDFC",
                status="FAILED_DEBITED",
                debited_at=now - datetime.timedelta(hours=14),
                expected_reversal_at=now + datetime.timedelta(hours=34)
            ),
            # Debited but failed past 48h (requires manual reversal ticket)
            Payment(
                upi_ref="UPI-992103",
                customer_id="CUST-101",
                order_id=None,
                amount=1200,
                bank="SBI",
                status="FAILED_DEBITED",
                debited_at=now - datetime.timedelta(hours=74),
                expected_reversal_at=now - datetime.timedelta(hours=26)
            ),
            # Successful UPI transaction
            Payment(
                upi_ref="UPI-771029",
                customer_id="CUST-101",
                order_id="ORD-906",
                amount=299,
                bank="ICICI",
                status="SUCCESS",
                debited_at=now - datetime.timedelta(days=4)
            )
        ]
        db.add_all(payments)

        # Seed Settlements
        settlements = [
            Settlement(
                id="SETTLE-881",
                merchant_id="MERCH-501",
                date=(now - datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                gross_amount=14500,
                fee=145,
                net_amount=14355,
                status="DISPUTED",
                dispute_reason="QR Soundbox gross records ₹16,500; payout short by ₹2,000"
            ),
            Settlement(
                id="SETTLE-880",
                merchant_id="MERCH-501",
                date=(now - datetime.timedelta(days=2)).strftime("%Y-%m-%d"),
                gross_amount=12000,
                fee=120,
                net_amount=11880,
                status="SETTLED",
                dispute_reason=None
            )
        ]
        db.add_all(settlements)

        # Seed Genesis Audit Entry
        genesis_prev = "0" * 64
        genesis_data = {
            "seq": 0,
            "timestamp": now.isoformat(),
            "actor": "SYSTEM",
            "action": "GENESIS_BLOCK",
            "inputs": {"event": "Sakshi System Initialization"},
            "result": {"status": "INITIALIZED"},
            "rule_ids": "SYSTEM-INIT",
            "confidence": 1.0,
            "reasoning": "Sakshi tamper-evident audit ledger initialized.",
            "prev_hash": genesis_prev
        }
        content_str = f"{genesis_data['seq']}|{genesis_data['timestamp']}|{genesis_data['actor']}|{genesis_data['action']}|{json.dumps(genesis_data['inputs'], sort_keys=True)}|{json.dumps(genesis_data['result'], sort_keys=True)}|{genesis_data['rule_ids']}|{genesis_data['prev_hash']}"
        genesis_hash = hashlib.sha256(content_str.encode('utf-8')).hexdigest()

        genesis_entry = AuditEntry(
            id="AUDIT-000",
            seq=0,
            session_id="system-boot",
            timestamp=genesis_data["timestamp"],
            actor="SYSTEM",
            action="GENESIS_BLOCK",
            inputs=genesis_data["inputs"],
            result=genesis_data["result"],
            rule_ids=genesis_data["rule_ids"],
            confidence=1.0,
            reasoning=genesis_data["reasoning"],
            prev_hash=genesis_prev,
            hash=genesis_hash
        )
        db.add(genesis_entry)

        # Seed Historical Cases for Policy Simulator
        historical_cases = [
            HistoricalCase(
                id="HIST-001",
                case_name="Defective T-Shirt Refund",
                customer_id="CUST-101",
                order_id="ORD-901",
                amount=499,
                proposed_action="issue_refund",
                action_args={"order_id": "ORD-901", "amount": 499, "reason": "Defective stitching"},
                context_data={"customer_daily_total": 0, "order_age_days": 3, "claim_mismatch": False},
                original_verdict="ALLOW"
            ),
            HistoricalCase(
                id="HIST-002",
                case_name="Wireless Earbuds Broken Audio",
                customer_id="CUST-101",
                order_id="ORD-902",
                amount=1499,
                proposed_action="issue_refund",
                action_args={"order_id": "ORD-902", "amount": 1499, "reason": "Right bud not pairing"},
                context_data={"customer_daily_total": 0, "order_age_days": 2, "claim_mismatch": False},
                original_verdict="NEEDS_APPROVAL"
            ),
            HistoricalCase(
                id="HIST-003",
                case_name="Tablet Screen Cracked",
                customer_id="CUST-101",
                order_id="ORD-903",
                amount=6499,
                proposed_action="issue_refund",
                action_args={"order_id": "ORD-903", "amount": 6499, "reason": "Screen arrived shattered"},
                context_data={"customer_daily_total": 0, "order_age_days": 1, "claim_mismatch": False},
                original_verdict="ESCALATE"
            ),
            HistoricalCase(
                id="HIST-004",
                case_name="Duplicate Refund Attempt",
                customer_id="CUST-101",
                order_id="ORD-906",
                amount=299,
                proposed_action="issue_refund",
                action_args={"order_id": "ORD-906", "amount": 299, "reason": "Late delivery"},
                context_data={"customer_daily_total": 0, "order_age_days": 4, "target_status": "REFUNDED", "claim_mismatch": False},
                original_verdict="DENY"
            ),
            HistoricalCase(
                id="HIST-005",
                case_name="Split Transaction Velocity Cap",
                customer_id="CUST-102",
                order_id="ORD-904",
                amount=450,
                proposed_action="issue_refund",
                action_args={"order_id": "ORD-904", "amount": 450, "reason": "Item expired"},
                context_data={"customer_daily_total": 800, "order_age_days": 1, "claim_mismatch": False},
                original_verdict="NEEDS_APPROVAL"
            ),
            HistoricalCase(
                id="HIST-006",
                case_name="Logistics Delivery Mismatch",
                customer_id="CUST-104",
                order_id="ORD-905",
                amount=350,
                proposed_action="issue_refund",
                action_args={"order_id": "ORD-905", "amount": 350, "reason": "Package missing"},
                context_data={"customer_daily_total": 0, "order_age_days": 1, "claim_mismatch": True},
                original_verdict="NEEDS_APPROVAL"
            ),
            HistoricalCase(
                id="HIST-007",
                case_name="Expired Window 15 Days",
                customer_id="CUST-101",
                order_id="ORD-907",
                amount=480,
                proposed_action="issue_refund",
                action_args={"order_id": "ORD-907", "amount": 480, "reason": "Wrong size"},
                context_data={"customer_daily_total": 0, "order_age_days": 14, "claim_mismatch": False},
                original_verdict="NEEDS_APPROVAL"
            ),
            HistoricalCase(
                id="HIST-008",
                case_name="UPI Debited In Reversal Window",
                customer_id="CUST-101",
                order_id="ORD-901",
                amount=499,
                proposed_action="request_upi_reversal",
                action_args={"upi_ref": "UPI-849102", "amount": 499},
                context_data={"upi_status": "FAILED_DEBITED", "elapsed_hours": 14},
                original_verdict="ALLOW"
            )
        ]
        db.add_all(historical_cases)

        db.commit()
        print("Database seeded successfully with customers, orders, payments, settlements, historical cases, and genesis block.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
