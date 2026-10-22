const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export const api = {
  // Chat
  sendMessage: async (sessionId: string, customerId: string, message: string) => {
    const res = await fetch(`${API_BASE}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, customer_id: customerId, message })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  // Trace History
  getTraceHistory: async (sessionId: string, sinceSeq: number = 0) => {
    const res = await fetch(`${API_BASE}/api/trace/history?session_id=${encodeURIComponent(sessionId)}&since_seq=${sinceSeq}`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  // SSE Trace Stream URL
  getTraceStreamUrl: (sessionId: string, sinceSeq: number = 0) => {
    return `${API_BASE}/api/trace/stream?session_id=${encodeURIComponent(sessionId)}&since_seq=${sinceSeq}`;
  },

  // Explainer
  explainAction: async (actionId: string) => {
    const res = await fetch(`${API_BASE}/api/actions/${encodeURIComponent(actionId)}/explain`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  // Audit Ledger
  getAuditLog: async (verify: boolean = false, sessionId?: string) => {
    let url = `${API_BASE}/api/audit?verify=${verify}`;
    if (sessionId) url += `&session_id=${encodeURIComponent(sessionId)}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  simulateTamper: async (seq: number) => {
    const res = await fetch(`${API_BASE}/api/audit/tamper`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ seq })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  restoreAuditLog: async () => {
    const res = await fetch(`${API_BASE}/api/audit/restore`, { method: "POST" });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  // Approval Queue
  getQueue: async () => {
    const res = await fetch(`${API_BASE}/api/queue`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  approveQueueItem: async (id: string, supervisorId: string = "SUPERVISOR-ANJALI") => {
    const res = await fetch(`${API_BASE}/api/queue/${id}/approve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ supervisor_id: supervisorId })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  rejectQueueItem: async (id: string, reason: string, supervisorId: string = "SUPERVISOR-ANJALI") => {
    const res = await fetch(`${API_BASE}/api/queue/${id}/reject`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason, supervisor_id: supervisorId })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  takeoverQueueItem: async (id: string, supervisorId: string = "SUPERVISOR-ANJALI") => {
    const res = await fetch(`${API_BASE}/api/queue/${id}/takeover`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ supervisor_id: supervisorId })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  // Undo Refund
  undoRefund: async (refundId: string, reason?: string) => {
    const res = await fetch(`${API_BASE}/api/refunds/${refundId}/undo`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ reason })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  // Policy & Autonomy Dial
  getPolicy: async () => {
    const res = await fetch(`${API_BASE}/api/policy`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  updatePolicy: async (autoResolveMax: number, supervisorApprovalMax: number, dailyCap?: number) => {
    const res = await fetch(`${API_BASE}/api/policy`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        auto_resolve_max: autoResolveMax,
        supervisor_approval_max: supervisorApprovalMax,
        daily_refund_cap_per_customer: dailyCap
      })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  simulatePolicy: async (autoMax: number, approvalMax: number) => {
    const res = await fetch(`${API_BASE}/api/policy/simulate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        proposed_tiers: { auto_resolve_max: autoMax, supervisor_approval_max: approvalMax }
      })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  // Evals Runner
  runEvals: async () => {
    const res = await fetch(`${API_BASE}/api/evals/run`, { method: "POST" });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  // Failure Injection
  getFailures: async () => {
    const res = await fetch(`${API_BASE}/api/admin/failures`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  toggleFailure: async (key: string, value: boolean) => {
    const res = await fetch(`${API_BASE}/api/admin/failures`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key, value })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  // Demo Scenarios
  getScenarios: async () => {
    const res = await fetch(`${API_BASE}/api/demo/scenarios`);
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },

  loadScenario: async (scenarioKey: string) => {
    const res = await fetch(`${API_BASE}/api/demo/scenario`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ scenario_key: scenarioKey })
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  }
};
