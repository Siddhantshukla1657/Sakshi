import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from ..db.database import SessionLocal
from ..db.models import Approval
from ..audit.logger import audit_logger
from ..tools.registry import execute_tool

class ApprovalManager:
    @staticmethod
    def create_approval(
        session_id: str,
        customer_id: str,
        action_type: str,
        amount: int,
        packet: Dict[str, Any],
        tool_args: Dict[str, Any]
    ) -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            approval_id = f"APPR-{int(datetime.datetime.now().timestamp() * 1000) % 100000}"
            now = datetime.datetime.now(datetime.timezone.utc)

            enriched_packet = dict(packet)
            enriched_packet["tool_args"] = tool_args

            approval = Approval(
                id=approval_id,
                session_id=session_id,
                customer_id=customer_id,
                action_type=action_type,
                amount=amount,
                status="PENDING",
                packet=enriched_packet,
                created_at=now
            )
            db.add(approval)
            db.commit()

            # Record in audit log
            audit_logger.append(
                session_id=session_id,
                actor="POLICY_ENGINE",
                action="QUEUE_APPROVAL",
                inputs={"approval_id": approval_id, "action": action_type, "amount": amount},
                result={"status": "PENDING_SUPERVISOR_DECISION"},
                rule_ids=packet.get("rule_ids", "R-TIER-02"),
                confidence=packet.get("confidence", 0.9),
                reasoning=f"Action requires human supervisor approval: {packet.get('issue', '')}"
            )

            return {
                "id": approval.id,
                "session_id": approval.session_id,
                "customer_id": approval.customer_id,
                "action_type": approval.action_type,
                "amount": approval.amount,
                "status": approval.status,
                "packet": approval.packet,
                "created_at": approval.created_at.isoformat()
            }
        finally:
            db.close()

    @staticmethod
    def list_queue() -> List[Dict[str, Any]]:
        db: Session = SessionLocal()
        try:
            records = db.query(Approval).order_by(Approval.created_at.desc()).all()
            return [
                {
                    "id": r.id,
                    "session_id": r.session_id,
                    "customer_id": r.customer_id,
                    "action_type": r.action_type,
                    "amount": r.amount,
                    "status": r.status,
                    "packet": r.packet,
                    "decided_by": r.decided_by,
                    "decided_at": r.decided_at.isoformat() if r.decided_at else None,
                    "rejection_reason": r.rejection_reason,
                    "created_at": r.created_at.isoformat()
                }
                for r in records
            ]
        finally:
            db.close()

    @staticmethod
    def approve(approval_id: str, supervisor_id: str = "SUPERVISOR-ANJALI") -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            approval = db.query(Approval).filter(Approval.id == approval_id).first()
            if not approval:
                return {"success": False, "error": f"Approval {approval_id} not found."}

            if approval.status != "PENDING":
                return {"success": False, "error": f"Approval is already in '{approval.status}' state."}

            now = datetime.datetime.now(datetime.timezone.utc)
            approval.status = "APPROVED"
            approval.decided_by = supervisor_id
            approval.decided_at = now

            tool_args = approval.packet.get("tool_args", {})
            action_type = approval.action_type

            # Execute the verified tool
            tool_result = execute_tool(action_type, tool_args, rule_ids="SUPERVISOR-SIGN-OFF")

            db.commit()

            # Record in audit log
            audit_logger.append(
                session_id=approval.session_id,
                actor="SUPERVISOR",
                action=f"APPROVE_{action_type.upper()}",
                inputs={"approval_id": approval_id, "tool_args": tool_args},
                result=tool_result,
                rule_ids="SUPERVISOR-AUTH",
                confidence=1.0,
                reasoning=f"Approved by supervisor {supervisor_id} after examining evidence packet."
            )

            return {
                "success": True,
                "approval_id": approval_id,
                "status": "APPROVED",
                "decided_by": supervisor_id,
                "tool_result": tool_result
            }
        finally:
            db.close()

    @staticmethod
    def reject(approval_id: str, reason: str, supervisor_id: str = "SUPERVISOR-ANJALI") -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            approval = db.query(Approval).filter(Approval.id == approval_id).first()
            if not approval:
                return {"success": False, "error": f"Approval {approval_id} not found."}

            if approval.status != "PENDING":
                return {"success": False, "error": f"Approval is already in '{approval.status}' state."}

            now = datetime.datetime.now(datetime.timezone.utc)
            approval.status = "REJECTED"
            approval.decided_by = supervisor_id
            approval.decided_at = now
            approval.rejection_reason = reason

            db.commit()

            # Record in audit log
            audit_logger.append(
                session_id=approval.session_id,
                actor="SUPERVISOR",
                action=f"REJECT_{approval.action_type.upper()}",
                inputs={"approval_id": approval_id, "reason": reason},
                result={"status": "REJECTED"},
                rule_ids="SUPERVISOR-REJECT",
                confidence=1.0,
                reasoning=f"Rejected by supervisor {supervisor_id}. Reason: {reason}"
            )

            return {
                "success": True,
                "approval_id": approval_id,
                "status": "REJECTED",
                "decided_by": supervisor_id,
                "reason": reason
            }
        finally:
            db.close()

    @staticmethod
    def takeover(approval_id: str, supervisor_id: str = "SUPERVISOR-ANJALI") -> Dict[str, Any]:
        db: Session = SessionLocal()
        try:
            approval = db.query(Approval).filter(Approval.id == approval_id).first()
            if not approval:
                return {"success": False, "error": f"Approval {approval_id} not found."}

            now = datetime.datetime.now(datetime.timezone.utc)
            approval.status = "TAKEN_OVER"
            approval.decided_by = supervisor_id
            approval.decided_at = now

            db.commit()

            audit_logger.append(
                session_id=approval.session_id,
                actor="SUPERVISOR",
                action="TAKEOVER_SESSION",
                inputs={"approval_id": approval_id},
                result={"status": "HUMAN_AGENT_CONNECTED"},
                rule_ids="SUPERVISOR-TAKEOVER",
                confidence=1.0,
                reasoning=f"Supervisor {supervisor_id} took manual control of live session {approval.session_id}."
            )

            return {
                "success": True,
                "approval_id": approval_id,
                "session_id": approval.session_id,
                "status": "TAKEN_OVER",
                "supervisor_id": supervisor_id
            }
        finally:
            db.close()

approval_manager = ApprovalManager()
