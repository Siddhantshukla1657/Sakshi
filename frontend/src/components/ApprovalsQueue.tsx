import React, { useState, useEffect } from "react";
import { UserCheck, CheckCircle2, XCircle, ArrowUpRight, ShieldAlert, Clock, AlertCircle } from "lucide-react";
import { api } from "../services/api";
import { ApprovalItem } from "../types";

interface ApprovalsQueueProps {
  onApprovalDecided: () => void;
}

export const ApprovalsQueue: React.FC<ApprovalsQueueProps> = ({ onApprovalDecided }) => {
  const [items, setItems] = useState<ApprovalItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [rejectReason, setRejectReason] = useState<{ [id: string]: string }>({});
  const [activeRejectId, setActiveRejectId] = useState<string | null>(null);

  const loadQueue = async () => {
    setIsLoading(true);
    try {
      const data = await api.getQueue();
      setItems(data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const handleApprove = async (id: string) => {
    try {
      await api.approveQueueItem(id);
      await loadQueue();
      onApprovalDecided();
    } catch (e: any) {
      alert(`Approval error: ${e.message}`);
    }
  };

  const handleReject = async (id: string) => {
    const reason = rejectReason[id] || "Disallowed by supervisor policy review";
    try {
      await api.rejectQueueItem(id, reason);
      setActiveRejectId(null);
      await loadQueue();
      onApprovalDecided();
    } catch (e: any) {
      alert(`Reject error: ${e.message}`);
    }
  };

  const handleTakeover = async (id: string) => {
    try {
      await api.takeoverQueueItem(id);
      await loadQueue();
      onApprovalDecided();
    } catch (e: any) {
      alert(`Takeover error: ${e.message}`);
    }
  };

  const pendingItems = items.filter((i) => i.status === "PENDING");
  const pastItems = items.filter((i) => i.status !== "PENDING");

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="bg-white border-ink-3 p-4 rounded-lg shadow-brutal flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="font-heading font-black text-xl text-ink flex items-center gap-2">
            <UserCheck className="text-navy" />
            Supervisor Approval Cockpit
          </h2>
          <p className="text-xs font-mono text-ink-muted">
            Inspect mid-value and high-risk actions queued by the deterministic policy engine.
          </p>
        </div>

        <button
          onClick={loadQueue}
          disabled={isLoading}
          className="btn-press bg-cream hover:bg-white text-ink border-ink-2 px-3 py-1.5 text-xs font-heading font-bold rounded shadow-brutal-sm"
        >
          {isLoading ? "Refreshing..." : "Refresh Queue"}
        </button>
      </div>

      {/* Active Pending Approvals */}
      <div className="space-y-4">
        <h3 className="font-heading font-bold text-sm text-ink uppercase tracking-wider flex items-center gap-2">
          <span>Pending Approvals ({pendingItems.length})</span>
        </h3>

        {pendingItems.length === 0 ? (
          <div className="bg-cream border-ink-2 p-8 rounded-lg shadow-brutal text-center font-mono">
            <div className="w-12 h-12 rounded-full bg-mint border-2 border-ink mx-auto flex items-center justify-center mb-2 shadow-brutal-sm">
              ✓
            </div>
            <h4 className="font-bold text-sm text-ink">Nothing Waiting in Queue</h4>
            <p className="text-xs text-ink-muted mt-1">
              "Nothing waiting. The agent is handling everything within autonomous limits."
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {pendingItems.map((item) => (
              <div
                key={item.id}
                className="bg-yellow-50 border-ink-3 rounded-lg shadow-brutal p-4 flex flex-col justify-between font-mono"
              >
                <div>
                  {/* Top Badge Row */}
                  <div className="flex items-center justify-between border-b border-ink-2 pb-2 mb-3">
                    <span className="font-bold text-xs text-ink bg-warning px-2 py-0.5 rounded border border-ink">
                      {item.id}
                    </span>
                    <span className="bg-white text-ink text-xs font-bold px-2 py-0.5 rounded border border-ink shadow-brutal-sm">
                      ₹{item.amount}
                    </span>
                  </div>

                  {/* Customer & Issue */}
                  <div className="space-y-2 mb-3">
                    <div>
                      <span className="text-[10px] text-ink-muted uppercase">Customer / Session:</span>
                      <p className="text-xs font-bold text-ink">{item.customer_id} ({item.session_id})</p>
                    </div>

                    <div>
                      <span className="text-[10px] text-ink-muted uppercase">Issue Summary:</span>
                      <p className="text-xs font-semibold text-ink bg-white border border-ink p-2 rounded">
                        {item.packet.issue}
                      </p>
                    </div>

                    <div>
                      <span className="text-[10px] text-ink-muted uppercase">Suggested Next Step:</span>
                      <p className="text-xs text-ink-muted italic">
                        {item.packet.suggested_step}
                      </p>
                    </div>
                  </div>

                  {/* Evidence Snapshot */}
                  <div className="bg-white border border-ink p-2.5 rounded text-[11px] mb-4 space-y-1">
                    <span className="font-bold text-ink block text-[10px] uppercase text-ink-muted">Evidence Packet:</span>
                    <pre className="text-[10px] text-ink overflow-x-auto">
                      {JSON.stringify(item.packet.evidence, null, 2)}
                    </pre>
                  </div>
                </div>

                {/* Supervisor Action Buttons */}
                <div className="pt-3 border-t border-ink-2 space-y-2">
                  {activeRejectId === item.id ? (
                    <div className="space-y-2">
                      <input
                        type="text"
                        placeholder="Enter rejection reason..."
                        value={rejectReason[item.id] || ""}
                        onChange={(e) => setRejectReason({ ...rejectReason, [item.id]: e.target.value })}
                        className="w-full bg-white border-ink-2 p-1.5 text-xs rounded"
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleReject(item.id)}
                          className="btn-press flex-1 bg-danger text-white text-xs font-heading font-bold py-1.5 rounded border-ink-2 shadow-brutal-sm"
                        >
                          Confirm Rejection
                        </button>
                        <button
                          onClick={() => setActiveRejectId(null)}
                          className="btn-press bg-white text-ink text-xs font-heading font-bold px-3 py-1.5 rounded border-ink-2"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      <button
                        onClick={() => handleApprove(item.id)}
                        className="btn-press flex-1 bg-mint hover:bg-mint-hover text-ink text-xs font-heading font-bold py-2 rounded border-ink-2 shadow-brutal flex items-center justify-center gap-1.5"
                      >
                        <CheckCircle2 size={14} />
                        <span>Approve ₹{item.amount}</span>
                      </button>

                      <button
                        onClick={() => setActiveRejectId(item.id)}
                        className="btn-press bg-white hover:bg-red-50 text-danger text-xs font-heading font-bold px-3 py-2 rounded border-ink-2 shadow-brutal-sm flex items-center gap-1"
                      >
                        <XCircle size={14} />
                        <span>Reject</span>
                      </button>

                      <button
                        onClick={() => handleTakeover(item.id)}
                        className="btn-press bg-navy hover:bg-blue-950 text-white text-xs font-heading font-bold px-3 py-2 rounded border-ink-2 shadow-brutal-sm flex items-center gap-1"
                      >
                        <span>Take Over</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Historical Decided Approvals */}
      {pastItems.length > 0 && (
        <div className="space-y-3 pt-4 border-t-2 border-ink">
          <h3 className="font-heading font-bold text-sm text-ink uppercase tracking-wider">
            Resolved Supervisor Decisions ({pastItems.length})
          </h3>
          <div className="bg-white border-ink-3 rounded-lg overflow-hidden shadow-brutal">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-cream border-b border-ink">
                <tr>
                  <th className="p-2.5">ID</th>
                  <th className="p-2.5">Action</th>
                  <th className="p-2.5">Amount</th>
                  <th className="p-2.5">Verdict</th>
                  <th className="p-2.5">Decided By</th>
                  <th className="p-2.5">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink-2">
                {pastItems.map((p) => (
                  <tr key={p.id} className="hover:bg-cream/40">
                    <td className="p-2.5 font-bold">{p.id}</td>
                    <td className="p-2.5">{p.action_type}</td>
                    <td className="p-2.5 font-bold">₹{p.amount}</td>
                    <td className="p-2.5">
                      <span className={`px-2 py-0.5 rounded border text-[10px] font-bold ${
                        p.status === "APPROVED"
                          ? "bg-mint text-ink border-ink"
                          : p.status === "REJECTED"
                          ? "bg-danger text-white border-ink"
                          : "bg-navy text-white border-ink"
                      }`}>
                        {p.status}
                      </span>
                    </td>
                    <td className="p-2.5 text-ink-muted">{p.decided_by || "SUPERVISOR"}</td>
                    <td className="p-2.5 text-ink-muted text-[11px]">{p.decided_at || p.created_at}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
