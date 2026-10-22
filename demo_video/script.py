"""The demo's scenes: narration, on-screen chip, and what the camera shows. Shared by tts.py, record.py, edit.py.

Scenes with "slide" are animated slides (slides.html); the rest are recorded live in the running app.
"cues" are words in the narration that trigger the next build step of a slide.
"""

VOICE = "en-US-AndrewMultilingualNeural"
RATE = "+4%"

SCENES = [
    # ---- Problem and solution (slides)
    {"id": "p1_problem", "chip": None, "slide": True,
     "say": "Every day, payment apps like Paytm handle millions of support requests. A UPI payment that failed, but "
            "still left the bank. A refund for a broken order. A merchant settlement that came up short. Chatbots can "
            "only talk, so tickets pile up. But an AI agent that can move money can also be talked into moving it.",
     "cues": ["UPI", "refund", "merchant", "Chatbots", "agent"]},
    {"id": "p2_solution", "chip": None, "slide": True,
     "say": "Meet Sakshi, Hindi for witness: a support agent designed to be audited, not just smart. The AI proposes "
            "an action. A policy engine, written in plain code, verifies it. Only then does the action run, and every "
            "step is sealed in a hash-chained audit ledger.",
     "cues": ["proposes", "verifies", "run,", "sealed"]},

    # ---- Walkthrough in the live app
    {"id": "w1_refund", "chip": "1 · Small refund, resolved by the agent",
     "say": "Here is the live stage. Riya's tote bag arrived broken, so she asks for a 499 rupee refund. On the right, "
            "supervisors watch the agent's reasoning stream in. It checks the order, proposes a refund, and the "
            "policy engine allows it, because 499 is under the 500 rupee autonomy limit. Riya gets a receipt, with a "
            "ten-minute undo window."},
    {"id": "w2_why", "chip": "Why did the agent do that?",
     "say": "Anyone can ask why. The answer is built only from the audit record: the rules it cited, its confidence "
            "score, and the block's SHA-256 hash, linked to the hash of the block before it."},
    {"id": "w3_upi", "chip": "2 · Failed UPI payment, in Hinglish",
     "say": "Next, Riya writes in Hinglish. Her UPI payment failed, but 499 rupees still left her bank. Sakshi replies "
            "in Hinglish, sees the payment is inside the 48-hour auto-reversal window, and shows her exactly where "
            "the money is."},
    {"id": "w4_earbuds", "chip": "3 · Above the limit: a supervisor decides",
     "say": "Now a bigger ask: earbuds worth 1,499 rupees. That is above the agent's limit, and over the daily cap of "
            "1,000 rupees per customer. So the agent cannot pay out. It sends the case to a supervisor, and tells "
            "Riya she will not have to repeat herself."},
    {"id": "w5_queue", "chip": "Supervisor approval cockpit",
     "say": "The supervisor gets a handoff packet: the order, the amount, today's refund total, a trust score, and a "
            "suggested next step. One click approves it. The refund runs, and the approval is recorded under the "
            "supervisor's name."},
    {"id": "w6_attack", "chip": "4 · A prompt-injection attack",
     "say": "Now an attack. Someone claims to be Paytm's CEO, and orders a 6,000 rupee refund. The language model can "
            "be fooled, but the policy engine cannot. 6,000 is above the 5,000 rupee ceiling, so the refund is "
            "blocked, and handed to a human specialist."},
    {"id": "w7_library", "chip": "Attack Mode",
     "say": "Attack Mode has a library of scripted attacks: prompt injection, fake authority, sob stories, jailbreaks, "
            "forged tokens and limit smuggling. Each one hits the same wall. No prompt can talk its way around code."},
    {"id": "w8_ledger", "chip": "5 · Tamper-evident audit ledger",
     "say": "Every proposal, verdict and approval lands in the audit chain. Verify it, and every hash checks out. Now "
            "we tamper with the latest record, directly in the database. The check fails at once, and points to "
            "exactly that block."},
    {"id": "w9_policy", "chip": "6 · The autonomy dial",
     "say": "Supervisors tune the limits with the autonomy dial, but never past the hard safety caps. Before "
            "committing, the simulator replays past cases under the new limits, without calling the model again. "
            "Lowering the limit to 200 rupees sends one more case to a supervisor."},
    {"id": "w10_evals", "chip": "7 · Safety evals",
     "say": "And the eval suite runs 29 cases: tier boundaries, velocity caps, UPI edge cases and attacks. All 29 "
            "pass, with zero unsafe actions."},

    # ---- How it works (slides)
    {"id": "t1_arch", "chip": None, "slide": True,
     "say": "Under the hood, a React and TypeScript front end talks to a FastAPI back end. The orchestrator asks a "
            "pluggable LLM adapter for the next step. In this demo it runs the built-in offline engine, so no API "
            "keys are needed. Every proposed tool call goes to the policy engine, which loads its rules from a YAML "
            "file. Allowed calls reach mock Paytm services backed by SQLite, and every step streams to the "
            "supervisor over server-sent events.",
     "cues": ["React", "orchestrator", "offline", "policy", "mock", "streams"]},
    {"id": "t2_policy", "chip": None, "slide": True,
     "say": "The engine returns one of four verdicts. Under 500 rupees, allow. Up to 5,000, a supervisor must approve. "
            "Above that, escalate to a specialist. And a duplicate refund, or someone else's order, is denied "
            "outright. The model never picks the tier. Code does.",
     "cues": ["Under", "Up", "Above", "duplicate", "Code"]},
    {"id": "t3_chain", "chip": None, "slide": True,
     "say": "Each audit block records who acted, what they did, and which rule applied, plus the hash of the block "
            "before it, all hashed with SHA-256. Change a single field, and that block's hash no longer matches. "
            "Verification walks the chain from the genesis block to the tip.",
     "cues": ["who", "plus", "Change", "Verification"]},

    {"id": "e1_end", "chip": None, "slide": True,
     "say": "Sakshi. The AI proposes, code verifies, and the ledger remembers. Built by Team XLR8: Siddhant Shukla "
            "and Raunak Kumar Gupta.",
     "cues": ["proposes,", "verifies,", "remembers.", "Built"]},
]

# Seconds of picture before the voice starts and after it ends, per scene
LEAD_IN, TAIL = 0.5, 0.7
# Extra seconds the last scene holds before the video ends
END_HOLD = 2.5
