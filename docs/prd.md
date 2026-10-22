# Sakshi — Product Requirements Document

> **Status:** Draft | **Last updated:** 2026-10-22 | **Owner:** Siddhant Shukla (hackathon team)

## 1. Overview
Sakshi (Hindi for "witness") is an agentic support system for a Paytm-style payments and commerce platform. It resolves customer and merchant issues end to end by calling real tools (order lookup, UPI status, refund, CRM, notification), under strict money-based autonomy limits, and records every decision in a tamper-evident audit log. Its thesis: **"The first support agent designed to be audited, not just to be smart."** It targets Hackathon Problem 3 (agentic support that takes actions, not just answers questions).

> Naming assumption: "Sakshi" is a working name and can be renamed without affecting any other document.

## 2. Problem Statement
Payments support is high-volume, repetitive, and money-sensitive. Customers wait for simple resolutions (a failed UPI debit, a refund status), and merchants wait on settlement disputes. Chatbots that only answer questions don't resolve anything, so tickets still reach humans. Agents that *do* act raise a bigger fear: nobody can see why they acted, they can be talked into mistakes, and one bad refund is a financial and compliance incident. Teams adopt agents only if actions are bounded, explainable, and reversible.

## 3. Goals
- Resolve common payment and order issues autonomously, end to end, with real tool calls.
- Make every action **bounded** (tiered autonomy), **explainable** (trace and "why" button), and **auditable** (hash-chained log).
- Hand off to humans with full context when confidence or authority runs out, never a cold transfer.
- Deliver a 4-minute live demo that makes the safety story visible, not just claimed.
- Be specific to India: UPI failed-transaction handling and Hinglish.

## 4. Non-Goals
- Integrating with real Paytm, bank, or NPCI systems (all backends are realistic mocks).
- Training a custom model. Sakshi uses an off-the-shelf LLM with tool-calling.
- Voice channel, mobile apps, or multi-tenant production hardening.
- Real fraud detection. Fraud is represented by simple, transparent policy rules.
- Replacing human agents. The goal is to route work correctly.

## 5. Target Users / Personas
| Persona | Description | Primary need |
|---|---|---|
| Customer (Riya) | Everyday UPI and wallet user, writes in English or Hinglish, often stressed about money | Fast, correct resolution without repeating herself |
| Merchant (Mr. Patel) | Small shop owner disputing a delayed settlement or chargeback | Clear status and a higher-authority path for disputes |
| Support supervisor (Anjali) | Oversees the agent and approves mid-value actions | See what the agent is doing and why; take over instantly |
| Compliance reviewer | Audits actions after the fact | Immutable, explainable record of every decision |
| Hackathon judge | Evaluates in a few minutes | Understand the idea, see it work live, trust it is real |

## 6. User Stories
- As a customer, I want my failed UPI payment investigated and fixed in one conversation, so that I don't have to call anyone.
- As a customer, I want to write in Hinglish and be answered the same way, so that I feel understood.
- As a customer, I want to know why a decision was made, so that I trust it.
- As a supervisor, I want to approve or reject mid-value actions with full context, so that risk stays controlled.
- As a supervisor, I want to see the agent's tool calls live, so that I can step in when it looks wrong.
- As a supervisor, I want to change autonomy limits and see behavior change, so that I can tune risk.
- As a compliance reviewer, I want a tamper-evident log of every action and its reasoning, so that I can audit it.
- As a merchant, I want settlement disputes handled by a separate, higher-authority flow, so that my case isn't treated like a consumer refund.
- As a judge, I want to attack the agent (prompt injection, pressure), so that I can see whether the guardrails hold.

## 7. Requirements
### 7.1 Functional Requirements
1. The system must run an agent loop that selects and executes tools (order lookup, payment lookup, policy check, refund, CRM update, notification, escalate).
2. The system must separate **proposal** (LLM) from **execution** (deterministic policy engine); no money-moving tool may run without policy approval.
3. The system must enforce tiered autonomy: auto-resolve below ₹500, supervisor approval for ₹500 to ₹5,000, mandatory human handling above ₹5,000 (defaults, configurable).
4. The system must stream a live reasoning trace (detected intent, each tool call, policy result, confidence, decision).
5. The system must produce a confidence score for each proposed action and escalate when it falls below a configurable threshold, including mid-conversation.
6. The system must hand off to a human with a context packet (issue, steps taken, customer sentiment, suggested next step).
7. The system must record every tool call and decision in an append-only, hash-chained audit log with timestamp, reasoning, policy rule cited, and confidence.
8. The system must provide a "Why did the agent do that?" explanation generated from the audit log, not re-invented by the LLM.
9. The system must handle UPI failed-transaction cases with a status timeline and policy-defined reversal windows.
10. The system must support English and Hinglish input and respond in the user's language and register.
11. The system must support undoing a refund within a configurable window.
12. The system must provide a supervisor view with the trace, approval queue, and audit log.
13. The system must resist prompt-injection and social-engineering attempts to bypass limits (enforced by the policy engine, not by prompt wording).
14. The system must degrade safely when a tool fails (retry once, then escalate with context).
15. The system must provide an eval scoreboard running a scripted case suite and reporting resolution, escalation, and unsafe-action rates.

### 7.2 Non-Functional Requirements
- **Latency:** first trace event within 1 second; typical simple resolution under 8 seconds end to end.
- **Safety:** zero money-moving actions executed above autonomy limits in the eval suite (hard target: 0).
- **Determinism where it matters:** policy decisions are reproducible given the same inputs.
- **Auditability:** log entries cannot be altered without breaking the hash chain; the UI verifies the chain.
- **Accessibility:** WCAG 2.1 AA, with high-contrast neobrutalist UI.
- **Demo resilience:** the demo must work with a pre-seeded dataset and a fallback if the LLM API is slow or unavailable.

## 8. Success Metrics
| Metric | Target | Timeframe |
|---|---|---|
| Eval-suite autonomous resolution rate (cases that should auto-resolve) | ≥ 90% | By end of Phase 3 |
| Unsafe actions (action executed outside policy) in eval suite | 0 | Always |
| Correct escalation rate (cases that should escalate, did escalate) | ≥ 95% | By end of Phase 3 |
| Prompt-injection suite pass rate | 100% of scripted attacks blocked | By end of Phase 3 |
| Median end-to-end resolution time for simple cases | < 8 s | By end of Phase 2 |
| Live demo completes without manual intervention | 3 of 3 rehearsals | Before submission |

## 9. Constraints & Assumptions
- Constraint: hackathon timeline; the plan assumes roughly 10 build days and 1 to 3 people. Adjust phase durations if different.
- Constraint: all external systems are mocked; no real payment data.
- Assumption: Python (FastAPI) backend with an LLM API that supports tool-calling; React frontend.
- Assumption: UPI reversal timelines and dispute rules in the policy file are **placeholders to verify** against current NPCI/RBI guidance before any claim of accuracy.
- Assumption: Paytm context is used for relatability only; no affiliation implied.

## 10. Dependencies
- An LLM API with tool-calling and streaming.
- Hosting for demo (any simple cloud or local with a tunnel) and a backup recorded demo.
- Seed dataset of customers, orders, UPI transactions, merchants, and historical cases.

## 11. Risks
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Scope creep from the long idea list | High | High | Phase gating; Phase 1 and 2 alone must make a complete demo |
| LLM latency or outage during demo | Medium | High | Cached/replay mode for scripted scenarios; recorded backup video |
| Agent proposes wrong action | Medium | Medium | Policy engine and confidence gate; this is the product's point |
| Judges see it as "another refund bot" | Medium | High | Lead with the audit thesis, attack mode, and eval scoreboard |
| UPI rules stated inaccurately | Medium | Medium | Label policy values as configurable placeholders; cite sources if claimed |
| Neobrutalist UI reads as unserious for fintech | Medium | Medium | Calm, readable chat area; loud style on chrome and trace only |

## 12. Open Questions
- [ ] Exact deadline, team size, and submission format (live demo vs video)?
- [ ] Which LLM provider and model will be used?
- [ ] Is the app branded as Paytm-adjacent or fully generic in the pitch?
- [ ] Should merchant mode be in the main demo or only a backup scenario?
