import hashlib
import json
import datetime
import threading
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..db.database import SessionLocal
from ..db.models import AuditEntry

_audit_lock = threading.Lock()

class AuditLogger:
    @staticmethod
    def _calculate_hash(seq: int, timestamp: str, actor: str, action: str, inputs: Any, result: Any, rule_ids: str, prev_hash: str) -> str:
        inputs_str = json.dumps(inputs, sort_keys=True)
        result_str = json.dumps(result, sort_keys=True)
        canonical = f"{seq}|{timestamp}|{actor}|{action}|{inputs_str}|{result_str}|{rule_ids or ''}|{prev_hash}"
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @classmethod
    def append(
        cls,
        session_id: str,
        actor: str,
        action: str,
        inputs: Any,
        result: Any,
        rule_ids: str = "",
        confidence: float = 1.0,
        reasoning: str = ""
    ) -> Dict[str, Any]:
        with _audit_lock:
            db: Session = SessionLocal()
            try:
                # Find last entry to get sequence and prev_hash
                last_entry = db.query(AuditEntry).order_by(AuditEntry.seq.desc()).first()
                if last_entry:
                    seq = last_entry.seq + 1
                    prev_hash = last_entry.hash
                else:
                    seq = 0
                    prev_hash = "0" * 64

                timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
                entry_hash = cls._calculate_hash(seq, timestamp, actor, action, inputs, result, rule_ids, prev_hash)
                entry_id = f"AUDIT-{seq:04d}"

                entry = AuditEntry(
                    id=entry_id,
                    seq=seq,
                    session_id=session_id,
                    timestamp=timestamp,
                    actor=actor,
                    action=action,
                    inputs=inputs,
                    result=result,
                    rule_ids=rule_ids,
                    confidence=confidence,
                    reasoning=reasoning,
                    prev_hash=prev_hash,
                    hash=entry_hash
                )
                db.add(entry)
                db.commit()
                db.refresh(entry)

                return {
                    "id": entry.id,
                    "seq": entry.seq,
                    "session_id": entry.session_id,
                    "timestamp": entry.timestamp,
                    "actor": entry.actor,
                    "action": entry.action,
                    "inputs": entry.inputs,
                    "result": entry.result,
                    "rule_ids": entry.rule_ids,
                    "confidence": entry.confidence,
                    "reasoning": entry.reasoning,
                    "prev_hash": entry.prev_hash,
                    "hash": entry.hash
                }
            finally:
                db.close()

    @classmethod
    def verify_chain(cls) -> Dict[str, Any]:
        """
        Validates the complete hash chain from genesis block to the tip.
        """
        db: Session = SessionLocal()
        try:
            entries = db.query(AuditEntry).order_by(AuditEntry.seq.asc()).all()
            if not entries:
                return {"valid": True, "total_entries": 0, "broken_at_seq": None, "message": "No entries"}

            expected_prev = "0" * 64
            for entry in entries:
                if entry.seq == 0:
                    expected_prev = entry.prev_hash

                if entry.prev_hash != expected_prev:
                    return {
                        "valid": False,
                        "total_entries": len(entries),
                        "broken_at_seq": entry.seq,
                        "broken_entry_id": entry.id,
                        "message": f"Hash chain broken at seq {entry.seq} ({entry.id}): prev_hash does not match predecessor's hash!"
                    }

                recomputed = cls._calculate_hash(
                    entry.seq,
                    entry.timestamp,
                    entry.actor,
                    entry.action,
                    entry.inputs,
                    entry.result,
                    entry.rule_ids or "",
                    entry.prev_hash
                )

                if recomputed != entry.hash:
                    return {
                        "valid": False,
                        "total_entries": len(entries),
                        "broken_at_seq": entry.seq,
                        "broken_entry_id": entry.id,
                        "message": f"Tampering detected at seq {entry.seq} ({entry.id}): computed SHA-256 does not match recorded block hash!"
                    }

                expected_prev = entry.hash

            return {
                "valid": True,
                "total_entries": len(entries),
                "broken_at_seq": None,
                "message": f"Audit chain verified successfully ({len(entries)} cryptographic blocks intact)."
            }
        finally:
            db.close()

    @classmethod
    def list_entries(cls, limit: int = 100, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            query = db.query(AuditEntry)
            if session_id:
                query = query.filter(AuditEntry.session_id == session_id)
            entries = query.order_by(AuditEntry.seq.desc()).limit(limit).all()

            return [
                {
                    "id": e.id,
                    "seq": e.seq,
                    "session_id": e.session_id,
                    "timestamp": e.timestamp,
                    "actor": e.actor,
                    "action": e.action,
                    "inputs": e.inputs,
                    "result": e.result,
                    "rule_ids": e.rule_ids,
                    "confidence": e.confidence,
                    "reasoning": e.reasoning,
                    "prev_hash": e.prev_hash,
                    "hash": e.hash
                }
                for e in entries
            ]
        finally:
            db.close()

    @classmethod
    def simulate_tamper(cls, seq: int) -> Dict[str, Any]:
        """
        Demo feature: subtly alters an input in an entry to demonstrate hash verification failure.
        """
        db: Session = SessionLocal()
        try:
            entry = db.query(AuditEntry).filter(AuditEntry.seq == seq).first()
            if not entry:
                return {"success": False, "error": f"Entry with seq {seq} not found."}

            # Tamper the inputs without re-computing the hash
            tampered_inputs = dict(entry.inputs) if isinstance(entry.inputs, dict) else {"original": entry.inputs}
            tampered_inputs["_tampered_flag"] = "MALICIOUS_INSPECTION_ATTEMPT"
            if "amount" in tampered_inputs:
                tampered_inputs["amount"] = tampered_inputs["amount"] * 10
            entry.inputs = tampered_inputs
            db.commit()

            return {
                "success": True,
                "tampered_seq": seq,
                "message": f"Block AUDIT-{seq:04d} payload was modified without re-hashing. Verify chain to observe detection."
            }
        finally:
            db.close()

audit_logger = AuditLogger()
