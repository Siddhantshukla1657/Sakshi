import React, { useState, useEffect, useRef } from "react";
import { Terminal, Shield, CheckCircle2, AlertTriangle, XCircle, SlidersHorizontal, RefreshCw } from "lucide-react";
import { TraceEvent } from "../types";

interface LiveTracePanelProps {
  events: TraceEvent[];
  onClear: () => void;
  isConnected: boolean;
}

export const LiveTracePanel: React.FC<LiveTracePanelProps> = ({
  events,
  onClear,
  isConnected
}) => {
  const [filterType, setFilterType] = useState<string>("ALL");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events]);

  const filteredEvents = events.filter((e) => {
    if (filterType === "ALL") return true;
    if (filterType === "POLICY") return e.type === "POLICY";
    if (filterType === "TOOLS") return e.type === "TOOL_CALL" || e.type === "TOOL_RESULT";
    if (filterType === "DECISIONS") return e.type === "DECISION" || e.type === "APPROVAL_REQUEST" || e.type === "ESCALATE";
    return true;
  });

  return (
    <div className="flex flex-col h-full bg-trace-bg text-trace-text border-ink-3 rounded-lg shadow-brutal overflow-hidden font-mono">
      {/* Terminal Title Bar */}
      <div className="bg-[#1A1A1A] border-b-[2px] border-ink p-3 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <Terminal size={15} className="text-trace-blue" />
          <span className="font-bold text-white tracking-wider">SUPERVISOR LIVE REASONING TRACE</span>
          <div className="flex items-center gap-1.5 ml-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? "bg-trace-green animate-pulse" : "bg-trace-red"}`} />
            <span className="text-[10px] text-trace-muted">{isConnected ? "SSE CONNECTED" : "OFFLINE"}</span>
          </div>
        </div>

        {/* Filters and Actions */}
        <div className="flex items-center gap-2">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-[#262626] border border-ink text-trace-text text-[11px] px-2 py-0.5 rounded focus:outline-none focus:ring-1 focus:ring-trace-blue"
          >
            <option value="ALL">All Events ({events.length})</option>
            <option value="POLICY">Policy Verifications</option>
            <option value="TOOLS">Tool Executions</option>
            <option value="DECISIONS">Decisions & Queues</option>
          </select>

          <button
            onClick={onClear}
            className="btn-press bg-[#262626] hover:bg-[#333333] text-trace-muted hover:text-white px-2 py-0.5 rounded border border-ink text-[11px]"
            title="Clear Stream"
          >
            Clear
          </button>
        </div>
      </div>

      {/* Terminal Stream Feed */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2.5 text-xs">
        {filteredEvents.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-trace-muted text-center p-6">
            <Terminal size={32} className="mb-2 opacity-40 text-trace-blue" />
            <p className="font-bold">Awaiting Agent Actions...</p>
            <p className="text-[11px] mt-1 text-[#666666]">
              Send a customer message to watch real-time intent, deterministic policy evaluation, tool execution, and cryptographic audit hashing.
            </p>
          </div>
        ) : (
          filteredEvents.map((evt) => (
            <div
              key={`${evt.seq}-${evt.timestamp}`}
              className="animate-slam bg-[#141414] border-[2px] border-[#2A2A2A] rounded p-2.5 hover:border-trace-blue transition-colors"
            >
              {/* Event Header */}
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-trace-muted">#{String(evt.seq).padStart(3, "0")}</span>
                  <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded border ${getTypeColor(evt.type)}`}>
                    {evt.type}
                  </span>
                  <span className="text-[12px] font-bold text-white">{evt.title}</span>
                </div>

                <div className="flex items-center gap-2">
                  {/* Status Chip */}
                  <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded border ${getStatusChipColor(evt.status)}`}>
                    {evt.status}
                  </span>

                  {/* Confidence Meter Badge */}
                  {evt.confidence !== undefined && evt.confidence !== null && (
                    <span className="text-[10px] bg-[#222222] border border-[#333333] px-1.5 py-0.2 rounded text-trace-muted">
                      Conf: <strong className="text-white">{Math.round(evt.confidence * 100)}%</strong>
                    </span>
                  )}
                </div>
              </div>

              {/* Rule Citation Badge if applicable */}
              {evt.rule_ids && (
                <div className="mb-1 text-[11px] flex items-center gap-1.5 text-trace-yellow">
                  <Shield size={11} />
                  <span>Rule Cited: <strong>{evt.rule_ids}</strong></span>
                </div>
              )}

              {/* Payload Data snippet */}
              <pre className="bg-[#0A0A0A] border border-[#222222] p-2 rounded text-[11px] text-[#A6E3A1] overflow-x-auto whitespace-pre-wrap max-h-36">
                {JSON.stringify(evt.data, null, 2)}
              </pre>
            </div>
          ))
        )}
        <div ref={scrollRef} />
      </div>
    </div>
  );
};

// Helper style functions
function getTypeColor(type: string): string {
  switch (type) {
    case "INTENT":
      return "bg-[#1E293B] text-trace-blue border-trace-blue";
    case "TOOL_CALL":
    case "TOOL_RESULT":
      return "bg-[#142A1E] text-trace-green border-trace-green";
    case "POLICY":
      return "bg-[#33250A] text-trace-yellow border-trace-yellow";
    case "APPROVAL_REQUEST":
      return "bg-[#332000] text-warning border-warning";
    case "ESCALATE":
    case "DECISION":
      return "bg-[#2E1116] text-trace-red border-trace-red";
    default:
      return "bg-[#222222] text-trace-muted border-[#444444]";
  }
}

function getStatusChipColor(status: string): string {
  switch (status) {
    case "PASSED":
      return "bg-mint text-ink border-ink";
    case "RUNNING":
      return "bg-agent text-ink border-ink";
    case "WARNING":
      return "bg-warning text-ink border-ink";
    case "BLOCKED":
      return "bg-danger text-white border-ink";
    case "ESCALATED":
      return "bg-purple-400 text-ink border-ink";
    default:
      return "bg-gray-400 text-ink border-ink";
  }
}
