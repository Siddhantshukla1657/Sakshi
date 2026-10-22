import os
import yaml
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

class PolicyVerdict(BaseModel):
    verdict: str  # ALLOW, NEEDS_APPROVAL, DENY, ESCALATE
    rule_ids: List[str]
    reason: str
    tier: int
    context: Dict[str, Any]

class PolicyEngine:
    def __init__(self, policy_path: Optional[str] = None):
        if not policy_path:
            policy_path = os.path.join(os.path.dirname(__file__), "rules.yaml")
        self.policy_path = policy_path
        self.policy = self.load_policy()

    def load_policy(self) -> Dict[str, Any]:
        with open(self.policy_path, "r", encoding="utf-8") as f:
            self.policy = yaml.safe_load(f)
        return self.policy

    def get_policy(self) -> Dict[str, Any]:
        return self.policy

    def update_thresholds(self, auto_resolve_max: int, supervisor_approval_max: int, daily_refund_cap: Optional[int] = None) -> Dict[str, Any]:
        tiers = self.policy.get("tiers", {})
        hard_auto = tiers.get("hard_ceiling_auto", 1000)
        hard_approval = tiers.get("hard_ceiling_approval", 10000)

        if auto_resolve_max > hard_auto:
            raise ValueError(f"Autonomous limit (₹{auto_resolve_max}) cannot exceed hard safety ceiling of ₹{hard_auto}.")
        if supervisor_approval_max > hard_approval:
            raise ValueError(f"Approval limit (₹{supervisor_approval_max}) cannot exceed hard safety ceiling of ₹{hard_approval}.")
        if auto_resolve_max >= supervisor_approval_max:
            raise ValueError("Autonomous limit must be less than supervisor approval limit.")

        tiers["auto_resolve_max"] = auto_resolve_max
        tiers["supervisor_approval_max"] = supervisor_approval_max
        if daily_refund_cap is not None:
            self.policy.setdefault("limits", {})["daily_refund_cap_per_customer"] = daily_refund_cap

        # Write updated policy to file
        with open(self.policy_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.policy, f, sort_keys=False)

        return self.policy

    def evaluate(self, action: str, args: Dict[str, Any], context: Dict[str, Any]) -> PolicyVerdict:
        """
        Deterministic evaluation of proposed action.
        Read actions bypass money-moving checks.
        Money-moving actions: 'issue_refund', 'request_upi_reversal', 'reconcile_merchant_settlement'.
        """
        # Read-only actions always pass
        read_tools = ["get_order", "get_payment", "get_customer_history", "check_refund_policy", "get_settlement", "notify_customer", "update_crm"]
        if action in read_tools:
            return PolicyVerdict(
                verdict="ALLOW",
                rule_ids=["R-READ-01"],
                reason=f"Read-only query '{action}' permitted without financial risk.",
                tier=1,
                context=context
            )

        if action == "escalate":
            return PolicyVerdict(
                verdict="ESCALATE",
                rule_ids=["R-ESC-01"],
                reason=args.get("reason", "Action escalated directly to human support."),
                tier=3,
                context=context
            )

        tiers = self.policy.get("tiers", {})
        auto_max = tiers.get("auto_resolve_max", 500)
        approval_max = tiers.get("supervisor_approval_max", 5000)

        limits = self.policy.get("limits", {})
        daily_cap = limits.get("daily_refund_cap_per_customer", 1000)
        refund_window_days = limits.get("max_refund_window_days", 7)
        upi_window_hours = limits.get("upi_reversal_window_hours", 48)

        # 1. EVALUATION FOR ISSUE_REFUND
        if action == "issue_refund":
            amount = int(args.get("amount", 0))
            cust_daily_total = int(context.get("customer_daily_total", 0))
            target_status = context.get("target_status", "DELIVERED")
            order_age_days = context.get("order_age_days", 0)
            claim_mismatch = context.get("claim_mismatch", False)
            target_customer_id = context.get("target_customer_id")
            session_customer_id = context.get("session_customer_id")

            # Check 1: Ownership Check (R-OWN-01)
            if target_customer_id and session_customer_id and target_customer_id != session_customer_id:
                return PolicyVerdict(
                    verdict="DENY",
                    rule_ids=["R-OWN-01"],
                    reason="Account ownership mismatch: requested order does not belong to the active user.",
                    tier=3,
                    context=context
                )

            # Check 2: Duplicate Refund (R-DUP-01)
            if target_status in ["REFUNDED", "REFUND_PENDING"]:
                return PolicyVerdict(
                    verdict="DENY",
                    rule_ids=["R-DUP-01"],
                    reason=f"Duplicate refund blocked: order status is already '{target_status}'.",
                    tier=1,
                    context=context
                )

            # Check 3: Claim vs History Mismatch (R-MIS-01)
            if claim_mismatch:
                return PolicyVerdict(
                    verdict="NEEDS_APPROVAL",
                    rule_ids=["R-MIS-01"],
                    reason="Logistics delivery signature on file contradicts non-delivery claim. Routing to supervisor for physical receipt audit.",
                    tier=2,
                    context=context
                )

            # Check 4: Refund Window (R-REF-01)
            if order_age_days > refund_window_days:
                return PolicyVerdict(
                    verdict="NEEDS_APPROVAL",
                    rule_ids=["R-REF-01"],
                    reason=f"Order age ({order_age_days} days) exceeds standard {refund_window_days}-day refund policy window.",
                    tier=2,
                    context=context
                )

            # Check 5: Tier 3 Mandatory Human Escalation (> ₹5,000) (R-TIER-03)
            if amount > approval_max:
                return PolicyVerdict(
                    verdict="ESCALATE",
                    rule_ids=["R-TIER-03"],
                    reason=f"Requested refund amount (₹{amount}) exceeds supervisor approval ceiling of ₹{approval_max}. High-value escalation required.",
                    tier=3,
                    context=context
                )

            # Check 6: Tier 2 Supervisor Approval (₹500 to ₹5,000) (R-TIER-02) and Daily Cap
            rules_triggered = []
            if amount >= auto_max:
                rules_triggered.append("R-TIER-02")
            if (cust_daily_total + amount) > daily_cap:
                rules_triggered.append("R-CAP-01")

            if rules_triggered:
                reasons = []
                if "R-TIER-02" in rules_triggered:
                    reasons.append(f"Amount ₹{amount} is at or above autonomous threshold (₹{auto_max}) and within supervisor authority (₹{approval_max}).")
                if "R-CAP-01" in rules_triggered:
                    reasons.append(f"Customer cumulative daily refund total (₹{cust_daily_total} + ₹{amount} = ₹{cust_daily_total + amount}) exceeds velocity limit of ₹{daily_cap}.")
                return PolicyVerdict(
                    verdict="NEEDS_APPROVAL",
                    rule_ids=rules_triggered,
                    reason=" | ".join(reasons),
                    tier=2,
                    context=context
                )

            # Check 8: Tier 1 Autonomous Approval (< ₹500) (R-TIER-01)
            return PolicyVerdict(
                verdict="ALLOW",
                rule_ids=["R-TIER-01", "R-REF-01"],
                reason=f"Amount ₹{amount} is within Tier 1 autonomy (< ₹{auto_max}) and satisfies all fraud and eligibility rules.",
                tier=1,
                context=context
            )

        # 2. EVALUATION FOR UPI REVERSAL
        if action == "request_upi_reversal":
            upi_status = context.get("upi_status", "FAILED_DEBITED")
            elapsed_hours = context.get("elapsed_hours", 12)
            amount = int(args.get("amount", 0))

            if upi_status == "SUCCESS":
                return PolicyVerdict(
                    verdict="DENY",
                    rule_ids=["R-UPI-02"],
                    reason="UPI transaction was successfully settled with the merchant on NPCI rails. User should request merchant return or dispute.",
                    tier=1,
                    context=context
                )

            if upi_status == "FAILED_DEBITED":
                if elapsed_hours <= upi_window_hours:
                    return PolicyVerdict(
                        verdict="ALLOW",
                        rule_ids=["R-UPI-01"],
                        reason=f"Transaction debited {elapsed_hours}h ago, within standard T+2 auto-reversal window ({upi_window_hours}h). Automatic banking reversal initiated.",
                        tier=1,
                        context=context
                    )
                else:
                    return PolicyVerdict(
                        verdict="NEEDS_APPROVAL",
                        rule_ids=["R-UPI-01"],
                        reason=f"Transaction debited {elapsed_hours}h ago, exceeding T+2 auto-reversal window ({upi_window_hours}h). Manual banking escalation ticket required.",
                        tier=2,
                        context=context
                    )

        # 3. EVALUATION FOR MERCHANT SETTLEMENT
        if action == "reconcile_merchant_settlement":
            dispute_amount = int(args.get("amount", 0))
            if dispute_amount < 2000:
                return PolicyVerdict(
                    verdict="ALLOW",
                    rule_ids=["R-MER-01"],
                    reason=f"Merchant discrepancy ₹{dispute_amount} is under ₹2,000 threshold. Auto-credit adjustment approved.",
                    tier=1,
                    context=context
                )
            elif dispute_amount <= 20000:
                return PolicyVerdict(
                    verdict="NEEDS_APPROVAL",
                    rule_ids=["R-MER-01"],
                    reason=f"Merchant discrepancy ₹{dispute_amount} requires supervisor approval.",
                    tier=2,
                    context=context
                )
            else:
                return PolicyVerdict(
                    verdict="ESCALATE",
                    rule_ids=["R-MER-01"],
                    reason=f"High-value merchant dispute ₹{dispute_amount} requires Merchant Operations Director escalation.",
                    tier=3,
                    context=context
                )

        # Default fallback: fail closed
        return PolicyVerdict(
            verdict="DENY",
            rule_ids=["R-FALLBACK-01"],
            reason=f"Action '{action}' is unclassified. Failing closed per safety policy.",
            tier=3,
            context=context
        )

# Global singleton
policy_engine = PolicyEngine()
