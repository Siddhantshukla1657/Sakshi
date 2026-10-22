import React, { useState, useEffect } from "react";
import { ShieldCheck, ShieldAlert, RefreshCw, Lock, AlertTriangle, CheckCircle, Database } from "lucide-react";
import { api } from "../services/api";
import { AuditEntry } from "../types";

export const AuditLedger: React.FC = () => {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [verification, setVerification] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [tamperedSeq, setTamperedSeq] = useState<number | null>(null);

  const loadAuditLog = async (verify = true) => {
    setIsLoading(true);
    try {
      const data = await api.getAuditLog(verify);
      setEntries(data.entries || []);
      setVerification(data.verification || null);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAuditLog(true);
  }, []);

  const handleVerify = async () => {
    setIsVerifying(true);
    try {
      const data = await api.getAuditLog(true);
      setVerification(data.verification);
    } catch (e: any) {
      alert(`Verification error: ${e.message}`);
    } finally {
      setIsVerifying(false);
    }
  };

  const handleSimulateTamper = async () => {
    if (entries.length === 0) return;
    const target = entries[0].seq; // Tamper latest entry
    try {
      const res = await api.simulateTamper(target);
      setTamperedSeq(target);
      await loadAuditLog(true);
      alert(res.message);
    } catch (e: any) {
      alert(`Tamper error: ${e.message}`);
    }
  };

  const handleRestore = async () => {
    try {
      await api.restoreAuditLog();
      setTamperedSeq(null);
      await loadAuditLog(true);
      alert("Ledger restored to clean cryptographic seed state.");
    } catch (e: any) {
      alert(`Restore error: ${e.message}`);
    }
  };

  return (
    <div className="space-y-6">
      {/* Ledger Header & Controls */}
      <div className="bg-white border-ink-3 p-4 rounded-lg shadow-brutal flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="font-heading font-black text-xl text-ink flex items-center gap-2">
            <Lock className="text-mint fill-ink" />
            Tamper-Evident Cryptographic Ledger
          </h2>
          <p className="text-xs font-mono text-ink-muted">
            Append-only SHA-256 hash-chained blocks. Every tool proposal, policy verdict, and human approval is cryptographically anchored.
          </p>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleVerify}
            disabled={isVerifying}
            className="btn-press bg-mint hover:bg-mint-hover text-ink text-xs font-heading font-bold px-3 py-2 rounded border-ink-2 shadow-brutal flex items-center gap-1.5"
          >
            <ShieldCheck size={14} />
            <span>{isVerifying ? "Verifying SHA-256..." : "Verify Hash Chain"}</span>
          </button>

          <button
            onClick={handleSimulateTamper}
            className="btn-press bg-danger text-white text-xs font-heading font-bold px-3 py-2 rounded border-ink-2 shadow-brutal-sm flex items-center gap-1"
            title="Demonstrate tamper detection"
          >
            <AlertTriangle size={14} />
            <span>Simulate Tamper</span>
          </button>

          <button
            onClick={handleRestore}
            className="btn-press bg-cream hover:bg-white text-ink text-xs font-heading font-bold px-3 py-2 rounded border-ink-2 shadow-brutal-sm flex items-center gap-1"
            title="Reset DB to clean genesis state"
          >
            <RefreshCw size={14} />
            <span>Restore Genesis</span>
          </button>
        </div>
      </div>

      {/* Verification Banner */}
      {verification && (
        <div
          className={`border-ink-3 p-4 rounded-lg shadow-brutal font-mono text-xs flex items-center justify-between ${
            verification.valid
              ? "bg-mint text-ink"
              : "bg-danger text-white"
          }`}
        >
          <div className="flex items-center gap-3">
            {verification.valid ? (
              <CheckCircle size={24} className="text-ink" />
            ) : (
              <ShieldAlert size={24} className="text-white" />
            )}
            <div>
              <h4 className="font-heading font-black text-sm">
                {verification.valid ? "CHAIN INTEGRITY VERIFIED (PASS)" : "CRYPTOGRAPHIC TAMPERING DETECTED (FAIL)"}
              </h4>
              <p className="text-xs mt-0.5 opacity-90">{verification.message}</p>
            </div>
          </div>

          <div className="text-right">
            <span className="font-bold text-xs uppercase block">Verified Blocks:</span>
            <span className="text-lg font-heading font-black">{verification.total_entries} Blocks</span>
          </div>
        </div>
      )}

      {/* Audit Blocks Table */}
      <div className="bg-white border-ink-3 rounded-lg overflow-hidden shadow-brutal">
        <div className="p-3 bg-cream border-b-[2px] border-ink flex items-center justify-between font-mono text-xs font-bold">
          <span>Cryptographic Ledger Blocks ({entries.length} Total)</span>
          <span className="text-ink-muted text-[11px]">Algorithm: SHA-256 Canonical Pipe-Delimited</span>
        </div>

        <div className="divide-y-2 divide-ink overflow-x-auto">
          {entries.map((entry) => (
            <div
              key={entry.id}
              className={`p-3.5 font-mono text-xs transition-colors ${
                tamperedSeq === entry.seq ? "bg-red-50 border-l-8 border-danger" : "hover:bg-cream/40"
              }`}
            >
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <span className="bg-ink text-white font-bold text-xs px-2 py-0.5 rounded">
                    BLOCK #{entry.seq}
                  </span>
                  <span className="font-bold text-agent text-xs">{entry.id}</span>
                  <span className="text-ink-muted text-[11px]">• {entry.timestamp}</span>
                </div>

                <div className="flex items-center gap-2">
                  <span className="bg-cream border border-ink text-[11px] font-bold px-2 py-0.5 rounded">
                    Actor: {entry.actor}
                  </span>
                  <span className="bg-white border border-ink text-[11px] font-bold px-2 py-0.5 rounded">
                    Action: {entry.action}
                  </span>
                  {entry.rule_ids && (
                    <span className="bg-yellow-200 border border-ink text-[11px] font-bold px-2 py-0.5 rounded">
                      {entry.rule_ids}
                    </span>
                  )}
                </div>
              </div>

              {/* Reasoning */}
              <div className="bg-cream border border-ink p-2 rounded mb-2 text-[11px]">
                <strong className="text-ink-muted">Reasoning: </strong>
                <span>{entry.reasoning}</span>
              </div>

              {/* Hash Cryptography Details */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[10px] text-ink-muted bg-white border border-ink p-2 rounded">
                <div>
                  <span className="font-bold text-ink">Previous Hash: </span>
                  <span className="truncate block font-mono text-gray-600">{entry.prev_hash}</span>
                </div>
                <div>
                  <span className="font-bold text-ink">Block SHA-256: </span>
                  <span className="truncate block font-mono text-agent font-bold">{entry.hash}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
