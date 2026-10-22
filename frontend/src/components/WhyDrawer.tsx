import React, { useEffect, useState } from "react";
import { X, ShieldCheck, CheckCircle2, Hash, FileText, Cpu, Lock } from "lucide-react";
import { api } from "../services/api";

interface WhyDrawerProps {
  auditId: string | null;
  onClose: () => void;
}

export const WhyDrawer: React.FC<WhyDrawerProps> = ({ auditId, onClose }) => {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!auditId) return;
    setIsLoading(true);
    setError(null);
    api.explainAction(auditId)
      .then((res) => setData(res))
      .catch((err) => setError(err.message || "Failed to load explanation"))
      .finally(() => setIsLoading(false));
  }, [auditId]);

  if (!auditId) return null;

  return (
    <div className="fixed inset-0 z-50 bg-ink/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white border-ink-3 rounded-lg shadow-brutal-lg max-w-xl w-full max-h-[90vh] flex flex-col overflow-hidden animate-slam">
        {/* Drawer Header */}
        <div className="bg-yellow-100 border-b-[3px] border-ink p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-mint border-2 border-ink p-1 rounded">
              <ShieldCheck size={18} className="text-ink" />
            </div>
            <div>
              <h3 className="font-heading font-black text-base text-ink">
                Why Did Sakshi Take This Action?
              </h3>
              <p className="text-[11px] font-mono text-ink-muted">
                Factual audit explanation grounded in tamper-evident block records.
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="btn-press bg-white hover:bg-cream border-ink-2 p-1.5 rounded shadow-brutal-sm text-ink"
          >
            <X size={16} />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {isLoading && (
            <div className="py-8 text-center text-xs font-mono animate-pulse">
              Querying cryptographic ledger for block {auditId}...
            </div>
          )}

          {error && (
            <div className="p-3 bg-red-100 border-2 border-danger text-xs font-mono text-danger rounded">
              {error}
            </div>
          )}

          {data && data.found && (
            <>
              {/* Core Justification Statement */}
              <div className="bg-cream border-ink-2 p-4 rounded-lg shadow-brutal-sm">
                <span className="text-[10px] font-mono font-bold uppercase text-ink-muted block mb-1">
                  Agent Policy Justification
                </span>
                <p className="font-body text-sm font-semibold text-ink leading-relaxed">
                  "{data.reasoning}"
                </p>
              </div>

              {/* Rules Cited */}
              <div className="space-y-1.5">
                <span className="text-[11px] font-mono font-bold uppercase text-ink-muted flex items-center gap-1">
                  <FileText size={12} />
                  Governance Rules Cited
                </span>
                <div className="flex flex-wrap gap-2">
                  {data.rules_cited && data.rules_cited.map((r: string) => (
                    <span
                      key={r}
                      className="bg-yellow-200 text-ink border border-ink text-xs font-mono font-bold px-2 py-0.5 rounded shadow-brutal-sm"
                    >
                      {r}
                    </span>
                  ))}
                </div>
              </div>

              {/* Confidence and Authority Metrics */}
              <div className="grid grid-cols-2 gap-3 text-xs font-mono">
                <div className="bg-white border-ink-2 p-3 rounded shadow-brutal-sm">
                  <span className="text-[10px] text-ink-muted block mb-0.5">Confidence Score</span>
                  <strong className="text-base font-heading font-black text-ink">{data.confidence_percent}</strong>
                  <div className="w-full bg-cream h-2 border border-ink rounded-full mt-1 overflow-hidden">
                    <div
                      className="bg-mint h-full"
                      style={{ width: `${Math.round(data.confidence * 100)}%` }}
                    />
                  </div>
                </div>

                <div className="bg-white border-ink-2 p-3 rounded shadow-brutal-sm">
                  <span className="text-[10px] text-ink-muted block mb-0.5">Executing Actor</span>
                  <strong className="text-base font-heading font-black text-agent">{data.actor}</strong>
                  <span className="text-[10px] text-ink-muted block mt-1">Action: {data.action}</span>
                </div>
              </div>

              {/* Cryptographic Proof Card */}
              {data.cryptographic_proof && (
                <div className="bg-[#141414] text-trace-text border-2 border-ink p-3 rounded-lg font-mono text-[11px] space-y-1.5">
                  <div className="flex items-center justify-between border-b border-[#333] pb-1.5">
                    <span className="text-trace-green font-bold flex items-center gap-1">
                      <Lock size={12} />
                      Cryptographic Ledger Proof
                    </span>
                    <span className="text-trace-muted">Block #{data.cryptographic_proof.block_seq}</span>
                  </div>

                  <div className="text-[10px] space-y-1 text-trace-muted overflow-hidden">
                    <div>
                      <span>Block SHA-256: </span>
                      <span className="text-trace-yellow truncate block">{data.cryptographic_proof.sha256_hash}</span>
                    </div>
                    <div>
                      <span>Predecessor Hash: </span>
                      <span className="text-white truncate block">{data.cryptographic_proof.prev_hash}</span>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="bg-cream border-t-[3px] border-ink p-3 flex justify-end">
          <button
            onClick={onClose}
            className="btn-press bg-white hover:bg-cream border-ink-2 px-4 py-1.5 text-xs font-heading font-bold rounded shadow-brutal text-ink"
          >
            Close Explanation
          </button>
        </div>
      </div>
    </div>
  );
};
