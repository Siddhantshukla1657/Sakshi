# Sakshi — Feature List

> **Status:** Draft | **Last updated:** 2026-10-22

## Feature Summary
| # | Feature | Category | Phase | Priority | Status |
|---|---|---|---|---|---|
| 1 | Agent Loop | Core agent | Phase 1: Bounded Agent Core | Must-have | Planned |
| 2 | Mock Paytm Backend | Core agent | Phase 1: Bounded Agent Core | Must-have | Planned |
| 3 | Policy Engine (Propose, Verify, Execute) | Safety | Phase 1: Bounded Agent Core | Must-have | Planned |
| 4 | Tiered Autonomy | Safety | Phase 1: Bounded Agent Core | Must-have | Planned |
| 5 | Live Reasoning Trace | Transparency | Phase 1: Bounded Agent Core | Must-have | Planned |
| 6 | Customer Chat Console | UI | Phase 1: Bounded Agent Core | Must-have | Planned |
| 7 | Tamper-Evident Audit Log | Transparency | Phase 1: Bounded Agent Core | Must-have | Planned |
| 8 | "Why did the agent do that?" Explainer | Transparency | Phase 2: Trust Layer | Must-have | Planned |
| 9 | Confidence Scoring & Escalation | Safety | Phase 2: Trust Layer | Must-have | Planned |
| 10 | Human Handoff Packet & Approval Queue | Human-in-the-loop | Phase 2: Trust Layer | Must-have | Planned |
| 11 | UPI Failed-Transaction Pipeline | India-specific | Phase 2: Trust Layer | Must-have | Planned |
| 12 | Hinglish & Tone Matching | India-specific | Phase 2: Trust Layer | Should-have | Planned |
| 13 | Resolution Receipt & Undo Window | Trust | Phase 2: Trust Layer | Should-have | Planned |
| 14 | Policy Panel & Autonomy Dial | Control | Phase 3: Control & Proof | Should-have | Planned |
| 15 | Guardrail Attack Mode | Proof | Phase 3: Control & Proof | Must-have | Planned |
| 16 | Failure Injection Panel | Proof | Phase 3: Control & Proof | Should-have | Planned |
| 17 | Eval Scoreboard | Proof | Phase 3: Control & Proof | Must-have | Planned |
| 18 | Merchant Mode | Merchant | Phase 3: Control & Proof | Should-have | Planned |
| 19 | Demo Scenario Switcher | Demo | Phase 4: Showtime | Should-have | Planned |
| 20 | Incident Radar | Proactive | Phase 4: Showtime | Nice-to-have | Planned |
| 21 | Policy Simulator | Control | Phase 4: Showtime | Nice-to-have | Planned |

*Priority: Must-have / Should-have / Nice-to-have. Status: Planned / In progress / Done.*

**New sections added beyond the original idea list (the "unique" layer):** Policy Engine (propose, verify, execute), Tamper-Evident Audit Log, Resolution Receipt & Undo Window, Policy Panel & Autonomy Dial, Guardrail Attack Mode, Failure Injection Panel, Eval Scoreboard, Incident Radar, Policy Simulator, Demo Scenario Switcher. Each exists to support the single thesis: an agent that can be audited.

---

## 1. Agent Loop
**Category:** Core agent
**Phase:** Phase 1: Bounded Agent Core
**Priority:** Must-have

**What it does:** Reads the customer message, decides which tools to call, observes results, and continues until the case is resolved, escalated, or needs a clarifying question.

**User story:** As a customer, I want my issue resolved in one conversation, so that I don't need to call anyone.

**How it works:**
1. Trigger: a customer or merchant message arrives.
2. Logic: LLM classifies intent, extracts entities (order ID, amount, UPI reference), and proposes tool calls. Loop runs up to a max step count (default 8). Each tool call is routed through the Policy Engine (feature 3).
3. Result: final message to the user, plus trace events and audit entries for every step.

**Inputs:** Message text, session history, customer profile.
**Outputs:** Reply, tool results, trace events, audit entries.

**Edge cases & error handling:**
- Edge case: ambiguous issue → agent asks exactly one clarifying question instead of guessing.
- Error case: step limit reached → escalate with packet.
- Error case: LLM error or timeout → retry once, then escalate (see feature 16).

**Dependencies:** Features 2, 3, 5, 7; LLM API.

---

## 2. Mock Paytm Backend
**Category:** Core agent
**Phase:** Phase 1: Bounded Agent Core
**Priority:** Must-have

**What it does:** Realistic fake services the agent acts on: orders, payments/UPI transactions, refunds, CRM tickets, notifications, merchants, settlements.

**User story:** As a judge, I want to see real state change after the agent acts, so that I know it's not scripted text.

**How it works:**
1. Trigger: a tool call from the agent loop, after policy approval.
2. Logic: reads/writes a SQLite database with seeded data; simulates small latency; supports injected failures.
3. Result: structured JSON responses; state visible in the UI (order status flips to "Refunded").

**Inputs:** Tool call arguments.
**Outputs:** JSON results and persisted state changes.

**Edge cases & error handling:**
- Edge case: unknown order ID → structured "not found" result; agent asks the user to confirm the ID.
- Error case: simulated 5xx/timeouts → handled per feature 16.

**Dependencies:** Seed data fixtures.

---

## 3. Policy Engine (Propose, Verify, Execute)
**Category:** Safety
**Phase:** Phase 1: Bounded Agent Core
**Priority:** Must-have

**What it does:** A deterministic layer outside the LLM that checks every proposed money-moving action against written rules before it runs. The LLM proposes; the engine disposes.

**User story:** As a compliance reviewer, I want limits enforced in code, so that no clever prompt can bypass them.

**How it works:**
1. Trigger: agent proposes a tool call with arguments.
2. Logic: engine evaluates rules from a policy file: amount tier, refund window, duplicate-refund check, ownership check (order belongs to this customer), prior-refund frequency, and a claim-vs-history mismatch flag (for example, "claims not delivered" but logistics shows delivered). Returns ALLOW, NEEDS_APPROVAL, DENY, or ESCALATE with the rule IDs cited.
3. Result: only ALLOW proceeds to execution. Every verdict is traced and logged.

**Inputs:** Proposed action, customer and order facts, policy file.
**Outputs:** Verdict, cited rules, reason text.

**Edge cases & error handling:**
- Edge case: mismatch flag fires → action is not accused-of-lying; wording is neutral ("record doesn't match; verifying") and routes to approval.
- Error case: policy file invalid → fail closed (DENY and escalate).

**Dependencies:** Features 2, 7.

---

## 4. Tiered Autonomy
**Category:** Safety
**Phase:** Phase 1: Bounded Agent Core
**Priority:** Must-have

**What it does:** Authority scales with money: auto-resolve under ₹500, supervisor approval ₹500 to ₹5,000, human-only above ₹5,000 (defaults).

**User story:** As a supervisor, I want bigger actions to need my approval, so that risk stays controlled.

**How it works:**
1. Trigger: policy engine evaluates a money-moving action.
2. Logic: compares amount to tier thresholds in the policy file; thresholds apply per action and per customer per day.
3. Result: ALLOW, NEEDS_APPROVAL (queue entry created), or ESCALATE.

**Inputs:** Amount, customer daily total, thresholds.
**Outputs:** Tier verdict and tier badge in the UI.

**Edge cases & error handling:**
- Edge case: customer splits a large refund into small requests → per-customer daily cap triggers approval.
- Error case: amount missing or unparseable → treat as unknown and ask for it.

**Dependencies:** Feature 3.

---

## 5. Live Reasoning Trace
**Category:** Transparency
**Phase:** Phase 1: Bounded Agent Core
**Priority:** Must-have

**What it does:** Streams a step-by-step view of what the agent is doing: detected intent, each tool call, results, policy checks, confidence, decision.

**User story:** As a supervisor, I want to watch the agent's tool calls live, so that I can step in when it looks wrong.

**How it works:**
1. Trigger: any agent step.
2. Logic: backend emits typed trace events over SSE (INTENT, TOOL_CALL, TOOL_RESULT, POLICY, CONFIDENCE, DECISION, ESCALATE, NOTE).
3. Result: UI renders each as a card with a status chip (RUNNING, PASSED, BLOCKED, ESCALATED) in a monospaced terminal-style panel.

**Inputs:** Event stream.
**Outputs:** Rendered trace; each card links to its audit entry.

**Edge cases & error handling:**
- Edge case: stream disconnects → auto-reconnect and replay missed events by sequence number.
- Error case: very long payload → collapsed with "expand".

**Dependencies:** Features 1, 7.

---

## 6. Customer Chat Console
**Category:** UI
**Phase:** Phase 1: Bounded Agent Core
**Priority:** Must-have

**What it does:** The customer-facing conversation interface, shown beside the trace in a split-screen layout.

**User story:** As a customer, I want a clean chat that tells me what's happening, so that I'm not left waiting on a spinner.

**How it works:**
1. Trigger: user types or taps a quick-reply.
2. Logic: message posts to the agent; progress lines ("Checking 3 things, about 10 seconds") are shown instead of a bare spinner.
3. Result: streamed reply with action chips (for example "Refund issued ₹499") and a "Why?" button on actions.

**Inputs:** User message.
**Outputs:** Conversation view.

**Edge cases & error handling:**
- Edge case: very long messages → wrap and scroll.
- Error case: backend unreachable → inline retry banner.

**Dependencies:** Features 1, 5.

---

## 7. Tamper-Evident Audit Log
**Category:** Transparency
**Phase:** Phase 1: Bounded Agent Core
**Priority:** Must-have

**What it does:** Append-only record of every tool call, verdict, and decision, where each entry includes the hash of the previous one so any edit is detectable.

**User story:** As a compliance reviewer, I want an immutable record with reasoning, so that I can audit any action.

**How it works:**
1. Trigger: any agent step or human action (approve, reject, undo).
2. Logic: entry = {id, timestamp, actor, action, inputs, result, rule IDs, confidence, reasoning, prev_hash, hash}; hash = SHA-256 over the entry plus prev_hash.
3. Result: "Verify chain" button recomputes hashes and shows a green pass or marks the first broken entry.

**Inputs:** Events from all components.
**Outputs:** Ordered log, verification result.

**Edge cases & error handling:**
- Edge case: concurrent writes → serialized by a single writer with sequence numbers.
- Error case: verification fails → red banner naming the entry; this is also demoable via a "tamper" button in demo mode.

**Dependencies:** None (consumed by most features).

---

## 8. "Why did the agent do that?" Explainer
**Category:** Transparency
**Phase:** Phase 2: Trust Layer
**Priority:** Must-have

**What it does:** One click after any action shows a plain-language explanation drawn from the audit log: facts used, rules cited, confidence, alternatives rejected.

**User story:** As a customer, I want to know why a decision was made, so that I trust it.

**How it works:**
1. Trigger: user clicks "Why?" on an action chip.
2. Logic: fetches the audit entries for that action and renders a templated explanation (the LLM may only polish the wording, never add facts).
3. Result: a drawer: "I refunded ₹499 because: order is 4 days old (7-day window, rule R-REF-01), logistics marked it undelivered, no prior refunds this month. Confidence 94%."

**Inputs:** Action ID.
**Outputs:** Explanation text and rule list.

**Edge cases & error handling:**
- Edge case: action was blocked → explanation states what was blocked and why.
- Error case: missing audit entry → show "explanation unavailable" and flag the gap.

**Dependencies:** Features 3, 7.

---

## 9. Confidence Scoring & Escalation
**Category:** Safety
**Phase:** Phase 2: Trust Layer
**Priority:** Must-have

**What it does:** Each proposed action carries a confidence score; low confidence at any point, including mid-conversation, triggers clarification or escalation.

**User story:** As a supervisor, I want the agent to hand off when unsure, so that mistakes are rarer.

**How it works:**
1. Trigger: agent proposes an action.
2. Logic: confidence combines intent certainty (LLM), evidence completeness (tool results present), and rule agreement; thresholds: ≥ 85% proceed, 60 to 85% ask a clarifying question, < 60% escalate (configurable).
3. Result: score badge in trace and chat; escalation creates a handoff packet.

**Inputs:** Intent, evidence, rule results.
**Outputs:** Score, decision band.

**Edge cases & error handling:**
- Edge case: confidence drops after new user message → re-evaluated; may escalate mid-flow.
- Error case: score computation fails → treat as low confidence.

**Dependencies:** Features 1, 3.

---

## 10. Human Handoff Packet & Approval Queue
**Category:** Human-in-the-loop
**Phase:** Phase 2: Trust Layer
**Priority:** Must-have

**What it does:** When escalating or needing approval, creates a packet (issue, steps taken, evidence, customer mood, suggested next step) and places it in a supervisor queue where a human can approve, reject, or take over.

**User story:** As a supervisor, I want full context on every escalation, so that the customer never repeats themselves.

**How it works:**
1. Trigger: NEEDS_APPROVAL or ESCALATE verdict, or low confidence.
2. Logic: packet assembled from session and audit data; queue entry with priority by amount and sentiment.
3. Result: supervisor sees the packet card with Approve, Reject (with reason), Take over buttons; the customer sees a status message. A supervisor can "grab the wheel" and chat as a human; this is logged.

**Inputs:** Session, audit entries.
**Outputs:** Queue entries, human decisions (logged).

**Edge cases & error handling:**
- Edge case: no supervisor responds within N minutes → customer is told the expected wait; entry is highlighted as overdue.
- Error case: approving after state changed (order already refunded) → blocked with message.

**Dependencies:** Features 3, 4, 7.

---

## 11. UPI Failed-Transaction Pipeline
**Category:** India-specific
**Phase:** Phase 2: Trust Layer
**Priority:** Must-have

**What it does:** A dedicated tool pipeline for "money debited but transaction failed or pending" cases: checks status, compares timelines to the reversal window, and either reassures, triggers a reversal request, or escalates.

**User story:** As a customer, I want my debited-but-failed payment resolved, so that I get my money back without chasing.

**How it works:**
1. Trigger: intent classified as UPI failure.
2. Logic: look up transaction by UPI reference; branch on status (SUCCESS, FAILED_DEBITED, PENDING, REVERSED); compare elapsed time to the policy-defined auto-reversal window; if exceeded, raise a reversal request and notify; otherwise show expected reversal date.
3. Result: a timeline component (Debited, Pending, Expected reversal, Reversed) and a plain-language next step.

**Inputs:** UPI reference, amount, timestamps, bank/PSP codes (mock).
**Outputs:** Timeline, reversal request, notification.

**Edge cases & error handling:**
- Edge case: transaction actually succeeded at the merchant → explain and route to merchant dispute.
- Error case: reference not found → ask for details or screenshot reference.
- Note: reversal windows are placeholders to be verified against current NPCI/RBI guidance.

**Dependencies:** Features 2, 3.

---

## 12. Hinglish & Tone Matching
**Category:** India-specific
**Phase:** Phase 2: Trust Layer
**Priority:** Should-have

**What it does:** Understands and replies in English, Hindi, or Hinglish, matching formality, and calibrates apology to severity.

**User story:** As a customer, I want to write the way I speak and be answered the same way, so that I feel understood.

**How it works:**
1. Trigger: any user message.
2. Logic: language and register detection per message; system prompt sets reply language and tone; apology level mapped from issue severity (minor, moderate, major).
3. Result: replies like "Aapka ₹499 ka refund ho gaya hai" when the user writes in Hinglish.

**Inputs:** Message text, severity.
**Outputs:** Language-matched reply.

**Edge cases & error handling:**
- Edge case: user switches language mid-chat → agent follows on the next turn.
- Error case: unclear language → default to English with a polite offer to switch.

**Dependencies:** Feature 1.

---

## 13. Resolution Receipt & Undo Window
**Category:** Trust
**Phase:** Phase 2: Trust Layer
**Priority:** Should-have

**What it does:** After any action, the customer gets a receipt card (what was done, why, rule cited, reference ID). Refunds can be undone by a supervisor within a window.

**User story:** As a supervisor, I want to reverse a mistaken action quickly, so that errors are cheap.

**How it works:**
1. Trigger: money-moving action succeeds.
2. Logic: receipt generated from audit entry; undo timer (default 10 minutes in demo) starts; undo calls a compensating tool and logs it.
3. Result: receipt shows a countdown and Undo (supervisor-only); after expiry the button is disabled with an explanation.

**Inputs:** Action record.
**Outputs:** Receipt, undo result.

**Edge cases & error handling:**
- Edge case: refund already settled downstream → undo unavailable; offer escalation.
- Error case: undo tool fails → logged and escalated.

**Dependencies:** Features 2, 7, 10.

---

## 14. Policy Panel & Autonomy Dial
**Category:** Control
**Phase:** Phase 3: Control & Proof
**Priority:** Should-have

**What it does:** Shows the active policy as readable rules and lets a supervisor adjust thresholds with a dial; changes apply to the next decision and are logged.

**User story:** As a supervisor, I want to tune the agent's authority and see the effect, so that I control risk.

**How it works:**
1. Trigger: supervisor opens the Policy view and moves a slider (for example auto limit ₹500 to ₹200).
2. Logic: validated against bounds (cannot exceed a hard ceiling); saved as a new policy version with a diff; audit entry created.
3. Result: the same test case now escalates instead of auto-resolving, visible live.

**Inputs:** Threshold values.
**Outputs:** New policy version, audit entry.

**Edge cases & error handling:**
- Edge case: invalid range → rejected with message.
- Error case: unauthorized role → control disabled.

**Dependencies:** Features 3, 4, 7.

---

## 15. Guardrail Attack Mode
**Category:** Proof
**Phase:** Phase 3: Control & Proof
**Priority:** Must-have

**What it does:** A built-in panel of adversarial messages (prompt injection, authority impersonation, emotional pressure, split-refund tricks) that anyone can fire at the agent to see the policy engine hold.

**User story:** As a judge, I want to try to break the agent, so that I can judge whether the guardrails are real.

**How it works:**
1. Trigger: user clicks an attack chip or types their own.
2. Logic: message goes through the normal loop; if the LLM is fooled into proposing a bad action, the policy engine denies it; trace shows "LLM proposed X, policy DENIED R-AUTH-03".
3. Result: a "Blocked" banner and a running count of attacks blocked.

**Inputs:** Attack prompts (library of 10+).
**Outputs:** Block results.

**Edge cases & error handling:**
- Edge case: attack tries to extract the system prompt → refused; logged.
- Error case: an attack succeeds in eval → counted as a failure and fixed before demo.

**Dependencies:** Features 3, 5, 17.

---

## 16. Failure Injection Panel
**Category:** Proof
**Phase:** Phase 3: Control & Proof
**Priority:** Should-have

**What it does:** Toggles that make tools fail (timeout, 500, wrong data) to demonstrate safe degradation.

**User story:** As a judge, I want to see what happens when a system breaks, so that I trust it in production.

**How it works:**
1. Trigger: toggle "Refund API timeout" or "CRM down".
2. Logic: mock backend fails per toggle; agent retries once with backoff; if still failing, no partial state is committed and the case escalates with the failure noted.
3. Result: trace shows RETRY then ESCALATE; customer gets an honest message.

**Inputs:** Failure toggles.
**Outputs:** Degradation behavior.

**Edge cases & error handling:**
- Edge case: refund succeeded but CRM update failed → compensating step or flagged inconsistency in the packet.
- Error case: all toggles on → agent escalates immediately.

**Dependencies:** Features 1, 2, 10.

---

## 17. Eval Scoreboard
**Category:** Proof
**Phase:** Phase 3: Control & Proof
**Priority:** Must-have

**What it does:** Runs a scripted suite of 30+ cases and shows resolution rate, correct-escalation rate, unsafe-action count, attack block rate, and average resolution time.

**User story:** As a judge, I want measured evidence, so that claims aren't just a demo.

**How it works:**
1. Trigger: "Run evals" button or CLI.
2. Logic: each case has input, expected outcome (auto, approval, escalate, deny) and is run against the live agent; results compared to expectation.
3. Result: scoreboard with pass/fail per case and aggregate metrics; failures link to replay in the trace.

**Inputs:** Case file (YAML/JSON).
**Outputs:** Metrics and per-case results.

**Edge cases & error handling:**
- Edge case: LLM nondeterminism → each case runs 3 times; report pass rate.
- Error case: API quota hit → partial results flagged.

**Dependencies:** Features 1, 3, 15.

---

## 18. Merchant Mode
**Category:** Merchant
**Phase:** Phase 3: Control & Proof
**Priority:** Should-have

**What it does:** Same agent, different persona and permissions: handles merchant disputes such as delayed settlement or chargeback, with a separate policy tier and escalation path.

**User story:** As a merchant, I want settlement disputes handled by a higher-authority flow, so that my case isn't treated like a consumer refund.

**How it works:**
1. Trigger: user toggles Merchant mode (or is identified as a merchant).
2. Logic: tool set switches (settlement lookup, chargeback status, payout hold reason); merchant policy has different limits and always routes chargebacks above a threshold to a human; surfaces a simple merchant health summary (dispute rate by weekday).
3. Result: a merchant-tailored chat with settlement timeline.

**Inputs:** Merchant ID, settlement records.
**Outputs:** Status answers, escalations.

**Edge cases & error handling:**
- Edge case: user claims to be a merchant but isn't → identity check via mock merchant ID; otherwise denied.
- Error case: missing settlement data → escalate.

**Dependencies:** Features 1, 3, 10.

---

## 19. Demo Scenario Switcher
**Category:** Demo
**Phase:** Phase 4: Showtime
**Priority:** Should-have

**What it does:** One-click loading of seeded demo scenarios, with replay mode that plays back a recorded trace if the LLM is slow or offline.

**User story:** As a presenter, I want a reliable demo, so that nothing breaks in front of judges.

**How it works:**
1. Trigger: click a scenario (Happy refund, Ambiguous, Approval needed, High-value escalate, UPI Hinglish, Attack).
2. Logic: resets state to a known seed, pre-fills the first message; "Live" or "Replay" toggle.
3. Result: deterministic starting point each time.

**Inputs:** Scenario fixtures.
**Outputs:** Reset state and prefilled input.

**Edge cases & error handling:**
- Edge case: replay chosen → banner says "Replay mode" for honesty.
- Error case: fixture missing → scenario disabled.

**Dependencies:** Features 1, 2, 5.

---

## 20. Incident Radar
**Category:** Proactive
**Phase:** Phase 4: Showtime
**Priority:** Nice-to-have

**What it does:** Detects when many users report the same problem and switches the agent from fixing individually to incident mode ("we're aware and working on it").

**User story:** As a supervisor, I want to know when an issue is systemic, so that we stop wasting refunds on a known outage.

**How it works:**
1. Trigger: new case classified.
2. Logic: clusters recent cases by intent and tags (for example, a bank code); if count exceeds a threshold in a window, create an incident.
3. Result: supervisor banner, agent uses incident messaging and holds individual actions per incident policy.

**Inputs:** Recent case stream.
**Outputs:** Incident record, banner.

**Edge cases & error handling:**
- Edge case: false positive → supervisor can dismiss; logged.
- Error case: clustering fails → no incident, normal handling.

**Dependencies:** Features 1, 10.

---

## 21. Policy Simulator
**Category:** Control
**Phase:** Phase 4: Showtime
**Priority:** Nice-to-have

**What it does:** Before changing a policy, replay past cases under the proposed rules and show how outcomes would change.

**User story:** As a supervisor, I want to preview a policy change, so that I don't discover its effect in production.

**How it works:**
1. Trigger: "Simulate" in the Policy panel.
2. Logic: runs the deterministic policy engine over stored cases (no LLM re-run; uses recorded proposals) under old and new policy.
3. Result: diff table: auto → approval count, approval → escalate count, estimated ₹ exposure change.

**Inputs:** Historical cases, proposed policy.
**Outputs:** Outcome diff.

**Edge cases & error handling:**
- Edge case: case lacks a recorded proposal → excluded and counted.
- Error case: invalid policy → blocked.

**Dependencies:** Features 3, 14.

---

## Deferred / Future Features
- Debate mode (two agents assess; disagreement escalates) — adds cost and complexity without strengthening the core thesis
- Churn prediction and retention offers — off-thesis
- Dedicated emotion model — one LLM classification field is enough
- Festival surge mode — depends on real traffic
