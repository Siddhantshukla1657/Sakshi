# Sakshi — Todo

> **Last updated:** 2026-10-22. Checked off as completed; reflects actual system implementation.

## Phase 1: Bounded Agent Core
- [x] Scaffold repo (FastAPI backend, React + Vite + TS frontend, Docker Compose)
- [x] Define SQLite schema and seed data (customers, orders, payments, merchants, settlements, past cases)
- [x] Build Mock Paytm Backend services with realistic latency
- [x] Define tool schemas (`get_order`, `get_payment`, `get_customer_history`, `check_refund_policy`, `issue_refund`, `update_crm`, `notify_customer`, `escalate`)
- [x] Write policy YAML v1 (refund window, tiers ₹500 / ₹5,000, daily cap, ownership, duplicate refund, claim-vs-history flag)
- [x] Implement Policy Engine with verdicts and rule IDs
  - [x] Unit tests for every rule and tier boundary (499, 500, 5000, 5001)
- [x] Implement LLM adapter and Agent Orchestrator loop with step limit
- [x] Wire propose, verify, execute so write tools only run on ALLOW
- [x] Implement hash-chained Audit Log and `verify()`
- [x] Implement Trace Emitter and SSE endpoint with sequence numbers and replay
- [x] Build design tokens, Tailwind config, and base components (button, card, chip, input)
  - [x] Load Space Grotesk, DM Sans, and JetBrains Mono with fallback stacks
  - [x] Implement press-in button, focus ring, and reduced-motion handling
- [x] Build Customer Chat Console with streamed replies and progress lines
- [x] Build Trace panel (terminal-style cards with status chips)
- [x] Build project-specific components (trace card, status chip, tier badge, confidence meter)
- [x] Build Split Stage layout (chat left, trace right)
- [x] Happy-path test: ₹499 refund resolves end to end
- [x] Block test: ₹6,000 refund is denied regardless of phrasing

## Phase 2: Trust Layer
- [x] Implement explanation builder from audit entries and "Why?" drawer
- [x] Implement confidence scoring (intent, evidence, rule agreement) and bands
- [x] Add one-question clarification flow for ambiguous intent
- [x] Build handoff packet assembler and Approval Queue API
- [x] Build supervisor Approval Queue UI (approve, reject with reason, take over)
- [x] Implement UPI failed-transaction tools and status branching
  - [x] Build UPI timeline component
  - [x] Add reversal-window values to policy file (marked "verify against NPCI/RBI guidance")
- [x] Add language and register detection, Hinglish prompts, apology calibration
- [x] Implement Resolution Receipt and Undo Window with countdown
  - [x] Build receipt, handoff packet (sticky note), and Why? drawer components
- [x] Add progress transparency lines in chat
- [x] Write the 4-minute demo script and run it end to end

## Phase 3: Control & Proof
- [x] Build Policy Panel with readable rules, versioning, and diff
- [x] Build Autonomy Dial with hard ceiling validation and audit entry
- [x] Build Guardrail Attack Mode with 10+ attack prompts and "Blocked" counter
- [x] Add failure-injection toggles in mock backend and the panel
  - [x] Implement retry once then safe escalation; no partial commits
- [x] Write eval case file (30+ cases across auto, approval, escalate, deny, attack, failure)
- [x] Build Eval Runner (3 runs per case) and Scoreboard UI
- [x] Implement Merchant Mode (tools, policy tier, settlement timeline)
- [x] Fix any eval failures; confirm 0 unsafe actions

## Phase 4: Showtime
- [x] Build Demo Scenario Switcher with seed reset and Live/Replay toggle
- [x] Implement Policy Simulator (recorded proposals, outcome diff)
- [x] Root batch scripts: install.bat & run.bat for instant 1-click execution

## Backlog / Unscheduled
- [ ] Debate mode for borderline cases
- [ ] Churn and retention offers
- [ ] Festival surge mode
- [ ] Dark mode for the UI
