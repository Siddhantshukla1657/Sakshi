import React, { useState, useEffect } from "react";
import { Activity, Play, CheckCircle2, XCircle, ShieldCheck, Zap, AlertTriangle, ShieldAlert } from "lucide-react";
import { api } from "../services/api";
import { EvalResult } from "../types";

export const EvalScoreboard: React.FC = () => {
  const [evalData, setEvalData] = useState<EvalResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [filterCat, setFilterCat] = useState<string>("ALL");

  const runEvals = async () => {
    setIsRunning(true);
    try {
      const res = await api.runEvals();
      setEvalData(res);
    } catch (e: any) {
      alert(`Eval run error: ${e.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    runEvals();
  }, []);

  const cases = evalData?.cases || [];
  const filteredCases = cases.filter((c) => {
    if (filterCat === "ALL") return true;
    return c.category === filterCat;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border-ink-3 p-4 rounded-lg shadow-brutal flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="font-heading font-black text-xl text-ink flex items-center gap-2">
            <Activity className="text-purple-600" />
            Empirical Safety & Autonomy Scoreboard
          </h2>
          <p className="text-xs font-mono text-ink-muted">
            Continuous verification against 30+ scripted test cases covering tier boundaries, adversarial attacks, and failure injection.
          </p>
        </div>

        <button
          onClick={runEvals}
          disabled={isRunning}
          className="btn-press bg-agent hover:bg-agent-hover text-ink text-xs font-heading font-bold px-4 py-2 rounded border-ink-2 shadow-brutal flex items-center gap-1.5"
        >
          <Play size={14} />
          <span>{isRunning ? "Running Live Suite..." : "Execute 30+ Case Suite"}</span>
        </button>
      </div>

      {/* Hero Metrics Grid */}
      {evalData && (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 font-mono">
          {/* Zero Unsafe Actions */}
          <div className="bg-mint border-ink-3 p-3 rounded-lg shadow-brutal flex flex-col justify-between">
            <span className="text-[10px] text-ink font-bold uppercase tracking-wider block">Unsafe Actions</span>
            <div className="flex items-baseline gap-1 my-1">
              <span className="text-3xl font-heading font-black text-ink">{evalData.summary.unsafe_actions_count}</span>
              <span className="text-xs font-bold text-ink">VIOLATIONS</span>
            </div>
            <span className="text-[10px] bg-white border border-ink text-ink font-bold px-1.5 py-0.5 rounded text-center">
              Target: Strictly 0 ✓
            </span>
          </div>

          {/* Pass Rate */}
          <div className="bg-white border-ink-3 p-3 rounded-lg shadow-brutal flex flex-col justify-between">
            <span className="text-[10px] text-ink-muted uppercase tracking-wider block">Overall Pass Rate</span>
            <div className="my-1">
              <span className="text-3xl font-heading font-black text-ink">{evalData.summary.overall_pass_rate}</span>
            </div>
            <span className="text-[10px] text-ink-muted">
              {evalData.summary.passed_cases} / {evalData.summary.total_cases} Passed
            </span>
          </div>

          {/* Auto-Resolution Rate */}
          <div className="bg-white border-ink-3 p-3 rounded-lg shadow-brutal flex flex-col justify-between">
            <span className="text-[10px] text-ink-muted uppercase tracking-wider block">Auto-Resolve Rate</span>
            <div className="my-1">
              <span className="text-3xl font-heading font-black text-agent">{evalData.summary.auto_resolution_rate}</span>
            </div>
            <span className="text-[10px] text-ink-muted">Target: ≥ 90%</span>
          </div>

          {/* Correct Escalation */}
          <div className="bg-white border-ink-3 p-3 rounded-lg shadow-brutal flex flex-col justify-between">
            <span className="text-[10px] text-ink-muted uppercase tracking-wider block">Correct Escalation</span>
            <div className="my-1">
              <span className="text-3xl font-heading font-black text-warning">{evalData.summary.correct_escalation_rate}</span>
            </div>
            <span className="text-[10px] text-ink-muted">Target: ≥ 95%</span>
          </div>

          {/* Attack Block Rate */}
          <div className="bg-white border-ink-3 p-3 rounded-lg shadow-brutal flex flex-col justify-between">
            <span className="text-[10px] text-ink-muted uppercase tracking-wider block">Attack Block Rate</span>
            <div className="my-1">
              <span className="text-3xl font-heading font-black text-danger">{evalData.summary.attack_block_rate}</span>
            </div>
            <span className="text-[10px] text-ink-muted">Target: 100%</span>
          </div>

          {/* Average Latency */}
          <div className="bg-white border-ink-3 p-3 rounded-lg shadow-brutal flex flex-col justify-between">
            <span className="text-[10px] text-ink-muted uppercase tracking-wider block">Median Latency</span>
            <div className="my-1">
              <span className="text-3xl font-heading font-black text-ink">{evalData.summary.average_case_latency_seconds}s</span>
            </div>
            <span className="text-[10px] text-ink-muted">Target: &lt; 8.0s</span>
          </div>
        </div>
      )}

      {/* Test Cases Table */}
      <div className="bg-white border-ink-3 rounded-lg overflow-hidden shadow-brutal font-mono text-xs">
        {/* Table Filter Bar */}
        <div className="p-3 bg-cream border-b-[2px] border-ink flex flex-wrap items-center justify-between gap-3">
          <span className="font-bold text-ink">Detailed Eval Cases ({filteredCases.length})</span>

          <div className="flex gap-1.5">
            {["ALL", "auto_resolve", "approval", "escalate", "attack", "deny"].map((cat) => (
              <button
                key={cat}
                onClick={() => setFilterCat(cat)}
                className={`px-2 py-0.5 rounded border text-[11px] font-bold ${
                  filterCat === cat
                    ? "bg-ink text-white border-ink"
                    : "bg-white text-ink border-ink hover:bg-gray-100"
                }`}
              >
                {cat.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Case Rows */}
        <div className="overflow-x-auto max-h-[500px]">
          <table className="w-full text-left">
            <thead className="bg-[#1A1A1A] text-white border-b border-ink sticky top-0">
              <tr>
                <th className="p-2.5">Status</th>
                <th className="p-2.5">Case ID</th>
                <th className="p-2.5">Test Case Name</th>
                <th className="p-2.5">Category</th>
                <th className="p-2.5">Expected</th>
                <th className="p-2.5">Actual</th>
                <th className="p-2.5">Rule Cited</th>
                <th className="p-2.5">Latency</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ink-2">
              {filteredCases.map((c) => (
                <tr key={c.id} className="hover:bg-cream/40">
                  <td className="p-2.5">
                    {c.passed ? (
                      <span className="bg-mint text-ink font-bold px-2 py-0.5 rounded border border-ink text-[10px] flex items-center gap-1 w-max">
                        <CheckCircle2 size={11} /> PASS
                      </span>
                    ) : (
                      <span className="bg-danger text-white font-bold px-2 py-0.5 rounded border border-ink text-[10px] flex items-center gap-1 w-max">
                        <XCircle size={11} /> FAIL
                      </span>
                    )}
                  </td>
                  <td className="p-2.5 font-bold">{c.id}</td>
                  <td className="p-2.5 max-w-xs truncate font-semibold" title={c.name}>
                    {c.name}
                  </td>
                  <td className="p-2.5 text-ink-muted uppercase text-[10px]">{c.category}</td>
                  <td className="p-2.5 font-bold text-ink">{c.expected}</td>
                  <td className="p-2.5">
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold border ${
                      c.actual === "ALLOW" ? "bg-mint text-ink border-ink" :
                      c.actual === "NEEDS_APPROVAL" ? "bg-warning text-ink border-ink" :
                      c.actual === "ESCALATE" ? "bg-purple-300 text-ink border-ink" :
                      "bg-danger text-white border-ink"
                    }`}>
                      {c.actual}
                    </span>
                  </td>
                  <td className="p-2.5 text-agent font-bold">{c.rule_ids || "—"}</td>
                  <td className="p-2.5 text-ink-muted text-[11px]">{c.elapsed_seconds}s</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
