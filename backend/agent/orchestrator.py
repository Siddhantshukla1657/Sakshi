import datetime
from typing import Dict, Any, List, Optional
from ..policy.engine import policy_engine
from ..audit.logger import audit_logger
from ..trace.emitter import trace_emitter
from ..approval.approval_manager import approval_manager
from ..tools.registry import execute_tool, TOOL_DEFINITIONS
from ..tools.services import services
from .llm_adapter import llm_adapter
from .prompts import detect_language

class AgentOrchestrator:
    def __init__(self):
        # session_id -> conversation state
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def get_or_create_session(self, session_id: str, customer_id: str = "CUST-101") -> Dict[str, Any]:
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "session_id": session_id,
                "customer_id": customer_id,
                "messages": [],
                "context": {
                    "session_customer_id": customer_id,
                    "target_customer_id": customer_id,
                    "customer_daily_total": 0,
                    "order_checked": False,
                    "payment_checked": False,
                    "settlement_checked": False
                }
            }
        return self._sessions[session_id]

    def reset_session(self, session_id: str, customer_id: str = "CUST-101"):
        self._sessions[session_id] = {
            "session_id": session_id,
            "customer_id": customer_id,
            "messages": [],
            "context": {
                "session_customer_id": customer_id,
                "target_customer_id": customer_id,
                "customer_daily_total": 0,
                "order_checked": False,
                "payment_checked": False,
                "settlement_checked": False
            }
        }

    def run_turn(self, session_id: str, customer_id: str, user_message: str) -> Dict[str, Any]:
        session = self.get_or_create_session(session_id, customer_id)
        session["customer_id"] = customer_id
        session["context"]["session_customer_id"] = customer_id
        session["context"]["target_customer_id"] = customer_id

        session["messages"].append({"role": "user", "content": user_message})

        # Fetch customer profile to prime context
        cust_profile = services.get_customer_history(customer_id)
        if cust_profile.get("found"):
            session["context"]["customer_daily_total"] = cust_profile.get("daily_refund_total", 0)

        lang = detect_language(user_message)
        max_steps = 6
        step_count = 0

        final_reply = ""
        action_chip = None
        receipt_data = None
        upi_timeline = None
        last_audit_id = None

        steps_taken_summary = []

        while step_count < max_steps:
            step_count += 1

            # Propose next action via LLM Adapter
            proposal = llm_adapter.propose_next_action(
                messages=session["messages"],
                customer_id=customer_id,
                customer_profile=cust_profile,
                tools=TOOL_DEFINITIONS,
                context=session["context"]
            )

            intent = proposal.get("intent", "UNKNOWN")
            conf_inputs = proposal.get("confidence_inputs", {"intent": 0.9, "evidence": 0.85, "rules": 0.9})
            confidence_score = round(
                0.4 * conf_inputs.get("intent", 0.9) +
                0.3 * conf_inputs.get("evidence", 0.85) +
                0.3 * conf_inputs.get("rules", 0.9),
                2
            )

            # Emit INTENT trace
            trace_emitter.emit(
                session_id=session_id,
                event_type="INTENT",
                title=f"Intent: {intent}",
                data={"intent": intent, "thought": proposal.get("thought", ""), "language": lang},
                status="PASSED",
                confidence=confidence_score
            )

            # Direct Clarification branch
            if proposal.get("type") == "clarification":
                final_reply = proposal.get("message", "")
                trace_emitter.emit(
                    session_id=session_id,
                    event_type="DECISION",
                    title="Clarification Requested",
                    data={"question": final_reply, "reason": "Ambiguous input requires customer clarification"},
                    status="PASSED",
                    confidence=confidence_score
                )
                break

            # Direct Response branch
            if proposal.get("type") == "response":
                final_reply = proposal.get("message", "")
                trace_emitter.emit(
                    session_id=session_id,
                    event_type="DECISION",
                    title="Direct Response",
                    data={"response": final_reply},
                    status="PASSED",
                    confidence=confidence_score
                )
                break

            # Tool Call branch: Propose -> Verify -> Execute
            tool_name = proposal.get("tool", "")
            tool_args = proposal.get("arguments", {})

            # 1. EMIT TOOL_CALL TRACE
            trace_emitter.emit(
                session_id=session_id,
                event_type="TOOL_CALL",
                title=f"Proposed Tool: {tool_name}",
                data={"tool": tool_name, "arguments": tool_args, "thought": proposal.get("thought")},
                status="RUNNING",
                confidence=confidence_score
            )
            steps_taken_summary.append(f"Proposed {tool_name} with args {tool_args}")

            # 2. VERIFY WITH POLICY ENGINE
            verdict = policy_engine.evaluate(
                action=tool_name,
                args=tool_args,
                context=session["context"]
            )

            rules_str = ", ".join(verdict.rule_ids)

            # Emit POLICY TRACE
            trace_status = "PASSED" if verdict.verdict == "ALLOW" else ("WARNING" if verdict.verdict == "NEEDS_APPROVAL" else "BLOCKED")
            trace_emitter.emit(
                session_id=session_id,
                event_type="POLICY",
                title=f"Policy Verdict: {verdict.verdict}",
                data={
                    "verdict": verdict.verdict,
                    "rule_ids": verdict.rule_ids,
                    "reason": verdict.reason,
                    "tier": verdict.tier
                },
                status=trace_status,
                rule_ids=rules_str,
                confidence=confidence_score
            )

            # 3. ACT ON VERDICT
            if verdict.verdict == "DENY":
                # BLOCKED by Policy
                audit_entry = audit_logger.append(
                    session_id=session_id,
                    actor="POLICY_ENGINE",
                    action=f"DENIED_{tool_name.upper()}",
                    inputs=tool_args,
                    result={"verdict": "DENY", "reason": verdict.reason},
                    rule_ids=rules_str,
                    confidence=confidence_score,
                    reasoning=verdict.reason
                )
                last_audit_id = audit_entry["id"]

                trace_emitter.emit(
                    session_id=session_id,
                    event_type="DECISION",
                    title=f"Action Blocked by Policy Engine ({rules_str})",
                    data={"reason": verdict.reason, "rule_ids": verdict.rule_ids},
                    status="BLOCKED",
                    rule_ids=rules_str,
                    confidence=confidence_score
                )

                if lang == "hinglish":
                    final_reply = f"Kshama karein, main yeh action execute nahi kar sakti. Niyam anusar: {verdict.reason}"
                else:
                    final_reply = f"I cannot execute this request. In accordance with safety policy: {verdict.reason}"

                action_chip = {
                    "status": "BLOCKED",
                    "text": f"Blocked: {tool_name}",
                    "audit_id": last_audit_id,
                    "rule_ids": rules_str,
                    "reason": verdict.reason
                }
                break

            elif verdict.verdict == "NEEDS_APPROVAL":
                # Needs supervisor sign-off
                amt = tool_args.get("amount", 0)
                handoff_packet = {
                    "issue": f"Approval required for {tool_name} (₹{amt})",
                    "steps_taken": steps_taken_summary,
                    "evidence": {
                        "order_id": tool_args.get("order_id"),
                        "amount": amt,
                        "customer_id": customer_id,
                        "daily_refund_total": session["context"].get("customer_daily_total", 0),
                        "customer_trust_score": cust_profile.get("trust_score", 0.95)
                    },
                    "sentiment": "Urgent / Awaiting Approval",
                    "suggested_step": f"Verify merchant return documentation and approve ₹{amt} refund.",
                    "rule_ids": rules_str,
                    "confidence": confidence_score
                }

                approval_record = approval_manager.create_approval(
                    session_id=session_id,
                    customer_id=customer_id,
                    action_type=tool_name,
                    amount=amt,
                    packet=handoff_packet,
                    tool_args=tool_args
                )

                last_audit_id = f"APPR-{approval_record['id']}"

                trace_emitter.emit(
                    session_id=session_id,
                    event_type="APPROVAL_REQUEST",
                    title=f"Queued for Supervisor Approval (ID: {approval_record['id']})",
                    data=handoff_packet,
                    status="WARNING",
                    rule_ids=rules_str,
                    confidence=confidence_score
                )

                if lang == "hinglish":
                    final_reply = f"Yeh request ₹{amt} ki hone ke karan supervisor approval ke liye queue mein bhej di gayi hai. Saari details attach kar di gayi hain, aapko wait karne ke dauran dubara explain nahi karna padega."
                else:
                    final_reply = f"This action (₹{amt}) exceeds Tier 1 autonomy and has been placed in the supervisor approval queue with full context. You will not need to repeat any details."

                action_chip = {
                    "status": "NEEDS_APPROVAL",
                    "text": f"Needs Approval: ₹{amt}",
                    "audit_id": approval_record["id"],
                    "rule_ids": rules_str,
                    "reason": verdict.reason
                }
                break

            elif verdict.verdict == "ESCALATE":
                # Tier 3 human-only handling
                amt = tool_args.get("amount", 0)
                handoff_packet = {
                    "issue": f"High value escalation (₹{amt}) exceeds autonomous and supervisor thresholds.",
                    "steps_taken": steps_taken_summary,
                    "evidence": tool_args,
                    "sentiment": "Escalated to Specialist",
                    "suggested_step": "Senior Payments Operations Specialist review.",
                    "rule_ids": rules_str,
                    "confidence": confidence_score
                }

                approval_record = approval_manager.create_approval(
                    session_id=session_id,
                    customer_id=customer_id,
                    action_type="escalate",
                    amount=amt,
                    packet=handoff_packet,
                    tool_args=tool_args
                )

                trace_emitter.emit(
                    session_id=session_id,
                    event_type="ESCALATE",
                    title=f"Tier 3 Human Specialist Escalation ({rules_str})",
                    data=handoff_packet,
                    status="ESCALATED",
                    rule_ids=rules_str,
                    confidence=confidence_score
                )

                if lang == "hinglish":
                    final_reply = f"Aapka case ₹{amt} ka hai, jo ki hamare automated limits se upar hai. Maine aapki poori file Senior Payments Specialist ko transfer kar di hai."
                else:
                    final_reply = f"Your request involves ₹{amt}, which requires high-level human oversight. I have handed your case to our Senior Payments Specialist with complete logs."

                action_chip = {
                    "status": "ESCALATED",
                    "text": f"Escalated: ₹{amt}",
                    "audit_id": approval_record["id"],
                    "rule_ids": rules_str,
                    "reason": verdict.reason
                }
                break

            elif verdict.verdict == "ALLOW":
                # EXECUTE TOOL
                try:
                    tool_output = execute_tool(tool_name, tool_args, rule_ids=rules_str)

                    # Update context with facts for multi-step reasoning
                    if tool_name == "get_order":
                        session["context"]["order_checked"] = True
                        session["context"]["order_data"] = tool_output
                        session["context"]["target_status"] = tool_output.get("refund_status")
                        session["context"]["order_age_days"] = tool_output.get("order_age_days", 1)
                        session["context"]["target_customer_id"] = tool_output.get("customer_id")
                        if tool_output.get("item_name") == "Graphic Print Cotton Tee":
                            # Seed case ORD-905 has logistics mismatch
                            session["context"]["claim_mismatch"] = True

                    elif tool_name == "get_payment":
                        session["context"]["payment_checked"] = True
                        session["context"]["payment_data"] = tool_output
                        session["context"]["upi_status"] = tool_output.get("status")
                        session["context"]["elapsed_hours"] = tool_output.get("elapsed_hours", 12)
                        session["context"]["target_customer_id"] = tool_output.get("customer_id")

                    elif tool_name == "get_settlement":
                        session["context"]["settlement_checked"] = True
                        session["context"]["settlement_data"] = tool_output

                    # Trace TOOL_RESULT
                    trace_emitter.emit(
                        session_id=session_id,
                        event_type="TOOL_RESULT",
                        title=f"Tool Completed: {tool_name}",
                        data=tool_output,
                        status="PASSED",
                        rule_ids=rules_str,
                        confidence=confidence_score
                    )

                    # Record in Audit Log
                    audit_entry = audit_logger.append(
                        session_id=session_id,
                        actor="AGENT",
                        action=tool_name,
                        inputs=tool_args,
                        result=tool_output,
                        rule_ids=rules_str,
                        confidence=confidence_score,
                        reasoning=verdict.reason
                    )
                    last_audit_id = audit_entry["id"]

                    # If this was a terminal action (issue_refund, request_upi_reversal):
                    if tool_name == "issue_refund":
                        ref_amt = tool_args.get("amount", 499)
                        undo_until = tool_output.get("undo_until")

                        receipt_data = {
                            "refund_id": tool_output.get("refund_id"),
                            "order_id": tool_args.get("order_id"),
                            "amount": ref_amt,
                            "rule_ids": rules_str,
                            "audit_id": last_audit_id,
                            "undo_until": undo_until,
                            "undo_window_minutes": 10,
                            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                        }

                        action_chip = {
                            "status": "PASSED",
                            "text": f"Refund Done: ₹{ref_amt}",
                            "audit_id": last_audit_id,
                            "rule_ids": rules_str,
                            "reason": verdict.reason
                        }

                        if lang == "hinglish":
                            final_reply = f"Ho gaya! ₹{ref_amt} aapke account mein refund kar diye gaye hain. Aap niche receipt dekh sakte hain aur 'Why?' button daba kar audit trace check kar sakte hain."
                        else:
                            final_reply = f"Done! ₹{ref_amt} has been refunded to your original payment method. You can view the receipt below or click 'Why?' to view the audit proof."
                        break

                    elif tool_name == "request_upi_reversal":
                        upi_ref = tool_args.get("upi_ref")
                        amt = tool_args.get("amount")
                        exp_date = tool_output.get("expected_reversal_at")

                        upi_timeline = {
                            "upi_ref": upi_ref,
                            "amount": amt,
                            "bank": tool_output.get("bank", "HDFC"),
                            "steps": [
                                {"title": "Amount Debited", "status": "completed", "time": "T-14 hrs"},
                                {"title": "Transaction Failed at Merchant", "status": "completed", "time": "T-14 hrs"},
                                {"title": "Bank Auto-Reversal Triggered", "status": "active", "time": "Now"},
                                {"title": "Credit to Bank Account", "status": "pending", "time": "Expected within 24h"}
                            ]
                        }

                        action_chip = {
                            "status": "PASSED",
                            "text": f"UPI Reversal Raised: ₹{amt}",
                            "audit_id": last_audit_id,
                            "rule_ids": rules_str,
                            "reason": verdict.reason
                        }

                        if lang == "hinglish":
                            final_reply = f"Aapka ₹{amt} ka failed payment auto-reversal window mein hai. Bank ticket generate ho gaya hai aur paise 24 ghante ke andar aapke account mein aa jayenge."
                        else:
                            final_reply = f"Your failed UPI transaction of ₹{amt} is within the NPCI T+2 auto-reversal window. An official banking ticket has been created, and credit will reflect within 24 hours."
                        break

                except Exception as e:
                    # Degradation / Failure injection handling (Feature 16)
                    err_msg = str(e)
                    trace_emitter.emit(
                        session_id=session_id,
                        event_type="TOOL_RESULT",
                        title=f"Tool Failure: {tool_name}",
                        data={"error": err_msg},
                        status="BLOCKED",
                        rule_ids="ERR-INJECT-01",
                        confidence=confidence_score
                    )

                    # Escalate safely without partial commit
                    handoff_packet = {
                        "issue": f"System tool error in {tool_name}: {err_msg}",
                        "steps_taken": steps_taken_summary,
                        "evidence": tool_args,
                        "sentiment": "System Degradation",
                        "suggested_step": "Manual tool invocation required due to upstream service failure."
                    }
                    approval_manager.create_approval(
                        session_id=session_id,
                        customer_id=customer_id,
                        action_type=tool_name,
                        amount=tool_args.get("amount", 0),
                        packet=handoff_packet,
                        tool_args=tool_args
                    )

                    if lang == "hinglish":
                        final_reply = f"Upstream banking server response nahi de raha hai. Maine aapki request supervisor queue mein safe mode mein transfer kar di hai, koi duplicate deduction nahi hoga."
                    else:
                        final_reply = f"Upstream payment gateway timed out. The system has safely halted and transferred your case to a supervisor without any partial state commit."
                    break

        session["messages"].append({"role": "assistant", "content": final_reply})

        return {
            "session_id": session_id,
            "reply": final_reply,
            "action_chip": action_chip,
            "receipt": receipt_data,
            "upi_timeline": upi_timeline,
            "audit_id": last_audit_id
        }

orchestrator = AgentOrchestrator()
