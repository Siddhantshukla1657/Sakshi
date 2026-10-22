# Sakshi — Phases

> **Status:** Draft | **Last updated:** 2026-10-22

Duration assumes a ~10-day build with 1 to 3 people. Phases 1 and 2 together form a complete, submittable demo; Phases 3 and 4 add proof and wow.

## Roadmap Summary
| Phase | Name | Goal | Target duration |
|---|---|---|---|
| Phase 1 | Bounded Agent Core | A real agent resolves a refund end to end under policy limits, with live trace and audit log | Days 1-3 |
| Phase 2 | Trust Layer | Explainability, confidence escalation, human handoff, UPI pipeline, Hinglish, undo | Days 4-6 |
| Phase 3 | Control & Proof | Supervisors tune policy live; attacks, failures, and evals prove the safety claims | Days 7-8 |
| Phase 4 | Showtime | Incident awareness, policy simulation, demo switcher, polish, and pitch | Days 9-10 |

---

## Phase 1: Bounded Agent Core
**Goal:** A real agent resolves a refund end to end under policy limits, with a live reasoning trace and an audit log.

**Scope:**
- Mock Paytm backend (orders, payments, CRM, notifications) with seed data
- Agent loop with tool-calling
- Policy engine enforcing propose, verify, execute
- Tiered autonomy limits
- Live reasoning trace streamed to the UI
- Customer chat console
- Hash-chained audit log
- Neobrutalist design tokens and base components

**Out of scope for this phase:**
- Confidence scoring, handoff packets, explain button, Hinglish, UPI pipeline

**Deliverables:**
- Working happy-path refund (under ₹500) and a refusal above limit
- Split-screen: chat on the left, live trace on the right
- Audit log written for every step

**Dependencies:** LLM API key; seed data; chosen stack scaffolded.

**Exit criteria:** A scripted refund case runs live end to end, and a ₹6,000 refund request is blocked by the policy engine regardless of how the customer phrases it.

---

## Phase 2: Trust Layer
**Goal:** Make every decision explainable, escalate intelligently, and handle India-specific cases.

**Scope:**
- "Why did the agent do that?" explainer
- Confidence scoring and confidence-based escalation
- Human handoff context packet and supervisor approval queue
- UPI failed-transaction pipeline with timeline
- Hinglish support and tone matching
- Resolution receipt and undo window

**Out of scope for this phase:**
- Live policy editing, evals, merchant mode

**Deliverables:**
- Four demo scenarios working: happy path, ambiguous (clarifying question), mid-value approval, high-value escalation
- UPI "debited but failed" scenario in Hinglish

**Dependencies:** Phase 1 complete.

**Exit criteria:** The full 4-minute demo script runs without manual patching.

---

## Phase 3: Control & Proof
**Goal:** Prove the agent is safe, controllable, and robust.

**Scope:**
- Policy panel and autonomy dial
- Guardrail attack mode
- Failure injection panel
- Eval scoreboard
- Merchant mode (settlement dispute)

**Out of scope for this phase:**
- Policy simulator, incident radar

**Deliverables:**
- Judge can change a limit live and watch the same case flip from auto to escalate
- Scripted attack suite and tool-failure scenarios pass
- Eval scoreboard with real numbers

**Dependencies:** Phase 2 complete.

**Exit criteria:** Eval suite meets the targets in prd.md section 8, with 0 unsafe actions.

---

## Phase 4: Showtime
**Goal:** Polish, redundancy, and the extra wow features.

**Scope:**
- Demo scenario switcher with replay fallback
- Incident radar (systemic issue detection)
- Policy simulator (counterfactual replay on past cases)
- Pitch deck, backup video, three full rehearsals

**Out of scope for this phase:**
- New core capabilities

**Deliverables:**
- Rehearsed demo, backup recording, pitch narrative around the audit thesis

**Dependencies:** Phases 1 to 3.

**Exit criteria:** Three consecutive clean rehearsals and a submitted entry.

---

## Future / Not Yet Scheduled
- Debate mode between two assessing agents for borderline cases
- Churn prediction and retention offers
- Emotion model beyond a single LLM classification field
- Festival surge mode
- Voice channel
