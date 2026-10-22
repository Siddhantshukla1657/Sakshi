import React, { useState, useEffect } from "react";
import { Sparkles, Bug, CheckCircle, RefreshCw, AlertOctagon } from "lucide-react";
import { api } from "../services/api";

interface DemoSwitcherProps {
  onLoadScenario: (scenarioKey: string, message: string) => void;
}

export const DemoSwitcher: React.FC<DemoSwitcherProps> = ({ onLoadScenario }) => {
  const [scenarios, setScenarios] = useState<{ [key: string]: any }>({});
  const [failures, setFailures] = useState<{ [key: string]: boolean }>({
    refund_timeout: false,
    crm_down: false,
    db_error: false
  });
  const [activeScenario, setActiveScenario] = useState<string>("happy_refund");

  useEffect(() => {
    api.getScenarios().then(setScenarios).catch(console.error);
    api.getFailures().then(setFailures).catch(console.error);
  }, []);

  const handleSelectScenario = async (key: string) => {
    setActiveScenario(key);
    try {
      const res = await api.loadScenario(key);
      onLoadScenario(key, res.scenario.message);
    } catch (e: any) {
      alert(`Load scenario error: ${e.message}`);
    }
  };

  const handleToggleFailure = async (key: string) => {
    const nextVal = !failures[key];
    try {
      const updated = await api.toggleFailure(key, nextVal);
      setFailures(updated);
    } catch (e: any) {
      alert(`Toggle failure error: ${e.message}`);
    }
  };

  return (
    <div className="bg-white border-ink-3 rounded-lg shadow-brutal p-3 font-mono text-xs">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-ink-2 pb-2.5 mb-2.5">
        <div className="flex items-center gap-2">
          <Sparkles size={16} className="text-warning fill-ink" />
          <span className="font-heading font-black text-sm text-ink">DEMO SCENARIO SWITCHER (FEATURE 19)</span>
        </div>

        {/* Failure Injection Toggles */}
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-ink-muted uppercase font-bold flex items-center gap-1">
            <Bug size={12} className="text-danger" />
            Failure Injection:
          </span>

          <button
            onClick={() => handleToggleFailure("refund_timeout")}
            className={`px-2 py-0.5 rounded border text-[10px] font-bold transition-all ${
              failures.refund_timeout
                ? "bg-danger text-white border-ink animate-pulse"
                : "bg-cream text-ink border-ink hover:bg-gray-100"
            }`}
          >
            Bank Timeout 504 {failures.refund_timeout && "●"}
          </button>

          <button
            onClick={() => handleToggleFailure("crm_down")}
            className={`px-2 py-0.5 rounded border text-[10px] font-bold transition-all ${
              failures.crm_down
                ? "bg-danger text-white border-ink animate-pulse"
                : "bg-cream text-ink border-ink hover:bg-gray-100"
            }`}
          >
            CRM Down 503 {failures.crm_down && "●"}
          </button>
        </div>
      </div>

      {/* Scenarios Preset Chips */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        <span className="text-[10px] font-bold text-ink-muted uppercase whitespace-nowrap">Load Case:</span>

        {Object.entries(scenarios).map(([key, item]) => (
          <button
            key={key}
            onClick={() => handleSelectScenario(key)}
            className={`btn-press whitespace-nowrap px-2.5 py-1 rounded border text-[11px] font-bold flex items-center gap-1.5 transition-all ${
              activeScenario === key
                ? "bg-ink text-white border-ink shadow-brutal-sm"
                : "bg-cream text-ink border-ink hover:bg-white"
            }`}
          >
            <span>{item.title}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
