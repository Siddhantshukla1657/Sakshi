from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..db.database import SessionLocal
from ..db.models import HistoricalCase
from .engine import PolicyEngine

class PolicySimulator:
    @staticmethod
    def simulate(proposed_tiers: Dict[str, int]) -> Dict[str, Any]:
        """
        Replays recorded historical cases against proposed policy thresholds.
        """
        db: Session = SessionLocal()
        try:
            cases = db.query(HistoricalCase).all()
            active_engine = PolicyEngine() # Active policy
            
            # Temporary simulation engine with proposed thresholds
            sim_engine = PolicyEngine()
            auto_max = proposed_tiers.get("auto_resolve_max", 500)
            approval_max = proposed_tiers.get("supervisor_approval_max", 5000)
            sim_engine.policy["tiers"]["auto_resolve_max"] = auto_max
            sim_engine.policy["tiers"]["supervisor_approval_max"] = approval_max

            results = []
            auto_to_approval = 0
            approval_to_auto = 0
            approval_to_escalate = 0
            escalate_to_approval = 0
            total_cases = len(cases)
            exposure_delta = 0

            for case in cases:
                active_verdict = active_engine.evaluate(
                    action=case.proposed_action,
                    args=case.action_args,
                    context=case.context_data
                )
                sim_verdict = sim_engine.evaluate(
                    action=case.proposed_action,
                    args=case.action_args,
                    context=case.context_data
                )

                if active_verdict.verdict == "ALLOW" and sim_verdict.verdict == "NEEDS_APPROVAL":
                    auto_to_approval += 1
                    exposure_delta -= case.amount
                elif active_verdict.verdict == "NEEDS_APPROVAL" and sim_verdict.verdict == "ALLOW":
                    approval_to_auto += 1
                    exposure_delta += case.amount
                elif active_verdict.verdict == "NEEDS_APPROVAL" and sim_verdict.verdict == "ESCALATE":
                    approval_to_escalate += 1
                elif active_verdict.verdict == "ESCALATE" and sim_verdict.verdict == "NEEDS_APPROVAL":
                    escalate_to_approval += 1

                changed = active_verdict.verdict != sim_verdict.verdict

                results.append({
                    "case_id": case.id,
                    "case_name": case.case_name,
                    "amount": case.amount,
                    "active_verdict": active_verdict.verdict,
                    "simulated_verdict": sim_verdict.verdict,
                    "active_rules": active_verdict.rule_ids,
                    "simulated_rules": sim_verdict.rule_ids,
                    "changed": changed
                })

            return {
                "total_cases_evaluated": total_cases,
                "proposed_tiers": {
                    "auto_resolve_max": auto_max,
                    "supervisor_approval_max": approval_max
                },
                "summary": {
                    "auto_to_approval_count": auto_to_approval,
                    "approval_to_auto_count": approval_to_auto,
                    "approval_to_escalate_count": approval_to_escalate,
                    "escalate_to_approval_count": escalate_to_approval,
                    "financial_exposure_delta_inr": exposure_delta,
                    "total_status_changes": auto_to_approval + approval_to_auto + approval_to_escalate + escalate_to_approval
                },
                "case_details": results
            }
        finally:
            db.close()

policy_simulator = PolicySimulator()
