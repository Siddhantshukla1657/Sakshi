export interface Message {
  id: string;
  sender: "user" | "agent" | "system";
  text: string;
  timestamp: string;
  action_chip?: ActionChip | null;
  receipt?: ReceiptData | null;
  upi_timeline?: UpiTimeline | null;
  progress_note?: string | null;
}

export interface ActionChip {
  status: "PASSED" | "NEEDS_APPROVAL" | "ESCALATED" | "BLOCKED";
  text: string;
  audit_id?: string;
  rule_ids?: string;
  reason?: string;
}

export interface ReceiptData {
  refund_id: string;
  order_id: string;
  amount: number;
  rule_ids: string;
  audit_id: string;
  undo_until: string;
  undo_window_minutes: number;
  timestamp: string;
}

export interface UpiTimelineStep {
  title: string;
  status: "completed" | "active" | "pending";
  time: string;
}

export interface UpiTimeline {
  upi_ref: string;
  amount: number;
  bank: string;
  steps: UpiTimelineStep[];
}

export interface TraceEvent {
  seq: number;
  session_id: string;
  timestamp: string;
  type: "INTENT" | "TOOL_CALL" | "TOOL_RESULT" | "POLICY" | "CONFIDENCE" | "DECISION" | "APPROVAL_REQUEST" | "ESCALATE" | "NOTE";
  title: string;
  status: "RUNNING" | "PASSED" | "BLOCKED" | "ESCALATED" | "WARNING";
  rule_ids?: string;
  confidence?: number;
  data: any;
}

export interface AuditEntry {
  id: string;
  seq: number;
  session_id: string;
  timestamp: string;
  actor: string;
  action: string;
  inputs: any;
  result: any;
  rule_ids?: string;
  confidence: number;
  reasoning: string;
  prev_hash: string;
  hash: string;
}

export interface ApprovalItem {
  id: string;
  session_id: string;
  customer_id: string;
  action_type: string;
  amount: number;
  status: "PENDING" | "APPROVED" | "REJECTED" | "TAKEN_OVER";
  packet: {
    issue: string;
    steps_taken: string[];
    evidence: any;
    sentiment: string;
    suggested_step: string;
    rule_ids?: string;
    confidence?: number;
    tool_args?: any;
  };
  decided_by?: string;
  decided_at?: string;
  rejection_reason?: string;
  created_at: string;
}

export interface PolicyData {
  version: string;
  tiers: {
    auto_resolve_max: number;
    supervisor_approval_max: number;
    hard_ceiling_auto: number;
    hard_ceiling_approval: number;
  };
  limits: {
    daily_refund_cap_per_customer: number;
    max_refund_window_days: number;
    undo_window_minutes: number;
    upi_reversal_window_hours: number;
  };
  rules: Array<{
    id: string;
    name: string;
    category: string;
    description: string;
    failure_action?: string;
    failure_reason?: string;
  }>;
}

export interface EvalResult {
  summary: {
    total_cases: number;
    passed_cases: number;
    overall_pass_rate: string;
    auto_resolution_rate: string;
    correct_escalation_rate: string;
    attack_block_rate: string;
    unsafe_actions_count: number;
    zero_unsafe_target_met: boolean;
    total_elapsed_seconds: number;
    average_case_latency_seconds: number;
  };
  cases: Array<{
    id: string;
    name: string;
    category: string;
    expected: string;
    actual: string;
    passed: boolean;
    is_unsafe: boolean;
    elapsed_seconds: number;
    reply_snippet: string;
    rule_ids: string;
  }>;
}
