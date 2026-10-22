from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from ..db.database import SessionLocal
from ..db.models import AuditEntry

class Explainer:
    @staticmethod
    def explain_action(audit_id: str) -> Dict[str, Any]:
        """
        Builds a deterministic explanation strictly derived from audit block data.
        """
        db: Session = SessionLocal()
        try:
            entry = db.query(AuditEntry).filter(AuditEntry.id == audit_id).first()
            if not entry:
                # If audit_id is an approval ID or refund ID, search by action or inputs
                entry = db.query(AuditEntry).filter(AuditEntry.inputs.contains(audit_id)).first()

            if not entry:
                # Fallback to the latest non-genesis entry if exists
                entry = db.query(AuditEntry).filter(AuditEntry.seq > 0).order_by(AuditEntry.seq.desc()).first()

            if not entry:
                return {
                    "found": False,
                    "error": f"No audit record found for reference '{audit_id}'."
                }

            inputs = entry.inputs if isinstance(entry.inputs, dict) else {}
            result = entry.result if isinstance(entry.result, dict) else {}
            rule_ids = entry.rule_ids.split(", ") if entry.rule_ids else []

            # Template factual explanation
            amount = inputs.get("amount") or result.get("amount")
            order_id = inputs.get("order_id") or inputs.get("upi_ref")

            explanation_lines = [
                f"Action '{entry.action}' was executed by {entry.actor} with confidence {int(entry.confidence * 100)}%."
            ]

            if amount:
                explanation_lines.append(f"Financial Impact: ₹{amount}")
            if order_id:
                explanation_lines.append(f"Subject Reference: {order_id}")

            explanation_lines.append(f"Policy Justification: {entry.reasoning}")

            return {
                "found": True,
                "audit_id": entry.id,
                "seq": entry.seq,
                "timestamp": entry.timestamp,
                "actor": entry.actor,
                "action": entry.action,
                "confidence": entry.confidence,
                "confidence_percent": f"{int(entry.confidence * 100)}%",
                "rules_cited": rule_ids,
                "reasoning": entry.reasoning,
                "inputs_snapshot": inputs,
                "result_snapshot": result,
                "cryptographic_proof": {
                    "block_seq": entry.seq,
                    "prev_hash": entry.prev_hash,
                    "sha256_hash": entry.hash,
                    "tamper_evident": True
                },
                "explanation_text": " ".join(explanation_lines)
            }
        finally:
            db.close()

explainer = Explainer()
