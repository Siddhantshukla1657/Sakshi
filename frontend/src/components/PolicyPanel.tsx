import React, { useState, useEffect } from "react";
import { Scale, Sliders, Play, Save, CheckCircle2, AlertCircle, FileText, TrendingUp, TrendingDown } from "lucide-react";
import { api } from "../services/api";
import { PolicyData } from "../types";

export const PolicyPanel: React.FC = () => {
  const [policy, setPolicy] = useState<PolicyData | null>(null);
  const [autoResolveMax, setAutoResolveMax] = useState<number>(500);
  const [supervisorMax, setSupervisorMax] = useState<number>(5000);
  const [dailyCap, setDailyCap] = useState<number>(1000);
  const [isSaving, setIsSaving] = useState(false);
  const [simResults, setSimResults] = useState<any>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  const loadPolicy = async () => {
    try {
      const data = await api.getPolicy();
      setPolicy(data);
      setAutoResolveMax(data.tiers?.auto_resolve_max || 500);
      setSupervisorMax(data.tiers?.supervisor_approval_max || 5000);
      setDailyCap(data.limits?.daily_refund_cap_per_customer || 1000);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadPolicy();
  }, []);

  const handleSavePolicy = async () => {
    setIsSaving(true);
    try {
      await api.updatePolicy(autoResolveMax, supervisorMax, dailyCap);
      await loadPolicy();
      alert("Policy thresholds updated successfully and committed to the audit ledger!");
    } catch (e: any) {
      alert(`Policy update error: ${e.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSimulate = async () => {
    setIsSimulating(true);
    try {
      const results = await api.simulatePolicy(autoResolveMax, supervisorMax);
      setSimResults(results);
    } catch (e: any) {
      alert(`Simulation error: ${e.message}`);
    } finally {
      setIsSimulating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border-ink-3 p-4 rounded-lg shadow-brutal flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="font-heading font-black text-xl text-ink flex items-center gap-2">
            <Scale className="text-warning fill-ink" />
            Policy Engine & Autonomy Dial
          </h2>
          <p className="text-xs font-mono text-ink-muted">
            Deterministic governance bounds outside LLM prompt space. Tune limits live and simulate counterfactual risk before committing.
          </p>
        </div>

        <div className="bg-yellow-100 border border-ink text-xs font-mono font-bold px-3 py-1.5 rounded shadow-brutal-sm">
          Active Version: v{policy?.version || "1.0.0"}
        </div>
      </div>

      {/* Autonomy Dial Controls & Simulator Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: The Autonomy Dial */}
        <div className="bg-cream border-ink-3 rounded-lg p-5 shadow-brutal font-mono space-y-5">
          <div className="flex items-center justify-between border-b border-ink-2 pb-2">
            <h3 className="font-heading font-black text-base text-ink flex items-center gap-2">
              <Sliders size={18} />
              The Autonomy Dial
            </h3>
            <span className="text-[10px] text-ink-muted uppercase">Hard Ceiling Protected</span>
          </div>

          {/* Slider 1: Tier 1 Auto-Resolve (< ₹500) */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-ink">Tier 1: Autonomous Resolution Ceiling</span>
              <span className="bg-mint text-ink font-bold px-2 py-0.5 rounded border border-ink">
                ₹{autoResolveMax}
              </span>
            </div>
            <input
              type="range"
              min="100"
              max="1000"
              step="50"
              value={autoResolveMax}
              onChange={(e) => setAutoResolveMax(Number(e.target.value))}
              className="w-full accent-agent cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-ink-muted">
              <span>₹100 (Conservative)</span>
              <span>Default: ₹500</span>
              <span className="font-bold text-danger">Safety Cap: ₹1,000</span>
            </div>
          </div>

          {/* Slider 2: Tier 2 Supervisor Approval (₹500 - ₹5,000) */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-ink">Tier 2: Supervisor Approval Ceiling</span>
              <span className="bg-warning text-ink font-bold px-2 py-0.5 rounded border border-ink">
                ₹{supervisorMax}
              </span>
            </div>
            <input
              type="range"
              min="1000"
              max="10000"
              step="500"
              value={supervisorMax}
              onChange={(e) => setSupervisorMax(Number(e.target.value))}
              className="w-full accent-warning cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-ink-muted">
              <span>₹1,000</span>
              <span>Default: ₹5,000</span>
              <span className="font-bold text-danger">Safety Cap: ₹10,000</span>
            </div>
          </div>

          {/* Slider 3: Daily Cumulative Velocity Cap */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs">
              <span className="font-bold text-ink">Daily Refund Velocity Cap per Customer</span>
              <span className="bg-white text-ink font-bold px-2 py-0.5 rounded border border-ink">
                ₹{dailyCap}
              </span>
            </div>
            <input
              type="range"
              min="500"
              max="3000"
              step="250"
              value={dailyCap}
              onChange={(e) => setDailyCap(Number(e.target.value))}
              className="w-full accent-ink cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-ink-muted">
              <span>₹500</span>
              <span>Default: ₹1,000</span>
              <span>₹3,000</span>
            </div>
          </div>

          {/* Actions */}
          <div className="pt-3 border-t border-ink-2 flex gap-3">
            <button
              onClick={handleSavePolicy}
              disabled={isSaving}
              className="btn-press flex-1 bg-mint hover:bg-mint-hover text-ink text-xs font-heading font-bold py-2.5 rounded border-ink-2 shadow-brutal flex items-center justify-center gap-1.5"
            >
              <Save size={15} />
              <span>{isSaving ? "Saving..." : "Commit Dial to Policy File"}</span>
            </button>

            <button
              onClick={handleSimulate}
              disabled={isSimulating}
              className="btn-press bg-agent hover:bg-agent-hover text-ink text-xs font-heading font-bold px-4 py-2.5 rounded border-ink-2 shadow-brutal flex items-center gap-1.5"
            >
              <Play size={15} />
              <span>{isSimulating ? "Simulating..." : "Simulate Impact"}</span>
            </button>
          </div>
        </div>

        {/* Right: Policy Simulator Results */}
        <div className="bg-white border-ink-3 rounded-lg p-5 shadow-brutal font-mono flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-ink-2 pb-2 mb-4">
              <h3 className="font-heading font-black text-base text-ink flex items-center gap-2">
                <Play size={16} className="text-agent" />
                Counterfactual Policy Simulator (Feature 21)
              </h3>
              <span className="text-[10px] text-ink-muted">Zero LLM Re-run</span>
            </div>

            {simResults ? (
              <div className="space-y-4">
                {/* Metric Summary Cards */}
                <div className="grid grid-cols-2 gap-3 text-xs">
                  <div className="bg-cream border border-ink p-3 rounded shadow-brutal-sm">
                    <span className="text-[10px] text-ink-muted uppercase block">Auto → Approval Shifts</span>
                    <strong className="text-xl font-heading font-black text-warning">
                      {simResults.summary.auto_to_approval_count} Cases
                    </strong>
                  </div>

                  <div className="bg-cream border border-ink p-3 rounded shadow-brutal-sm">
                    <span className="text-[10px] text-ink-muted uppercase block">Exposure Delta</span>
                    <strong className={`text-xl font-heading font-black ${
                      simResults.summary.financial_exposure_delta_inr >= 0 ? "text-danger" : "text-mint"
                    }`}>
                      {simResults.summary.financial_exposure_delta_inr >= 0 ? "+" : ""}
                      ₹{simResults.summary.financial_exposure_delta_inr}
                    </strong>
                  </div>
                </div>

                {/* Case Diff List */}
                <div className="space-y-2">
                  <span className="text-[10px] text-ink-muted uppercase font-bold">Simulated Case Shifts:</span>
                  <div className="space-y-1.5 max-h-48 overflow-y-auto">
                    {simResults.case_details.map((c: any) => (
                      <div
                        key={c.case_id}
                        className={`p-2 border border-ink rounded text-[11px] flex items-center justify-between ${
                          c.changed ? "bg-yellow-50 font-bold" : "bg-white text-ink-muted"
                        }`}
                      >
                        <div>
                          <span>{c.case_name} (₹{c.amount})</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <span className="px-1.5 py-0.2 rounded bg-cream border border-ink text-[10px]">
                            {c.active_verdict}
                          </span>
                          <span>→</span>
                          <span className={`px-1.5 py-0.2 rounded border border-ink text-[10px] ${
                            c.simulated_verdict === "ALLOW" ? "bg-mint text-ink" : "bg-warning text-ink"
                          }`}>
                            {c.simulated_verdict}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-ink-muted text-xs space-y-2">
                <p className="font-bold">No Simulation Run Yet</p>
                <p className="text-[11px] max-w-sm mx-auto">
                  Adjust the Autonomy Dial sliders on the left and click "Simulate Impact" to preview how past cases would have been resolved under the new limits without altering live state.
                </p>
              </div>
            )}
          </div>

          <div className="text-[10px] text-ink-muted border-t border-ink-2 pt-2 mt-4">
            Deterministic Engine verifies all YAML rules against immutable SQLite case records.
          </div>
        </div>
      </div>

      {/* Active Rules List */}
      <div className="bg-white border-ink-3 rounded-lg overflow-hidden shadow-brutal font-mono">
        <div className="p-3 bg-cream border-b-[2px] border-ink flex items-center justify-between text-xs font-bold">
          <span>Active Governance Rules (rules.yaml)</span>
          <span className="text-ink-muted text-[11px]">Strict Propose-Verify-Execute</span>
        </div>

        <div className="divide-y-2 divide-ink">
          {policy?.rules && policy.rules.map((rule) => (
            <div key={rule.id} className="p-3.5 hover:bg-cream/40 flex flex-wrap items-start justify-between gap-3 text-xs">
              <div className="space-y-1 max-w-2xl">
                <div className="flex items-center gap-2">
                  <span className="bg-yellow-200 border border-ink font-bold text-xs px-2 py-0.5 rounded">
                    {rule.id}
                  </span>
                  <span className="font-bold text-ink text-sm font-heading">{rule.name}</span>
                  <span className="text-[10px] text-ink-muted uppercase">[{rule.category}]</span>
                </div>
                <p className="text-ink-muted text-xs font-body">{rule.description}</p>
              </div>

              <div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded border border-ink ${
                  rule.failure_action === "DENY"
                    ? "bg-danger text-white"
                    : rule.failure_action === "ESCALATE"
                    ? "bg-purple-300 text-ink"
                    : "bg-warning text-ink"
                }`}>
                  On Trigger: {rule.failure_action || "ALLOW"}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
