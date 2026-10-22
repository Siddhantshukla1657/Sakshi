import React from "react";
import { ShieldCheck, UserCheck, Terminal, ListOrdered, Scale, Activity, Flame, ShieldAlert } from "lucide-react";

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  role: "customer" | "supervisor";
  setRole: (role: "customer" | "supervisor") => void;
  pendingApprovalsCount: number;
}

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  setActiveTab,
  role,
  setRole,
  pendingApprovalsCount
}) => {
  return (
    <header className="border-b-[3px] border-ink bg-white sticky top-0 z-40 overflow-x-hidden">
      <div className="max-w-7xl mx-auto px-4 py-3 flex flex-wrap items-center justify-between gap-2 min-w-0">
        {/* Logo and Thesis */}
        <div className="flex items-center gap-3">
          <div className="bg-mint border-ink-3 shadow-brutal px-3 py-1 font-heading font-black text-2xl tracking-tight text-ink flex items-center gap-2">
            <span>साक्षी</span>
            <span className="text-sm font-mono font-bold bg-ink text-mint px-1.5 py-0.5 rounded">SAKSHI</span>
          </div>
          <div className="hidden sm:block">
            <h1 className="text-xs font-mono font-semibold text-ink-muted uppercase tracking-wider">
              Audited Agentic Support Platform
            </h1>
            <p className="text-[11px] font-mono text-ink">
              "Designed to be <span className="font-bold underline decoration-mint decoration-2">audited</span>, not just smart."
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1.5 overflow-x-auto py-1">
          <button
            onClick={() => setActiveTab("stage")}
            className={`btn-press px-3 py-1.5 text-xs font-heading font-bold flex items-center gap-1.5 border-ink-2 rounded ${
              activeTab === "stage"
                ? "bg-agent text-ink shadow-brutal"
                : "bg-cream text-ink hover:bg-white"
            }`}
          >
            <Terminal size={14} />
            <span>Live Stage</span>
          </button>

          <button
            onClick={() => setActiveTab("queue")}
            className={`btn-press px-3 py-1.5 text-xs font-heading font-bold flex items-center gap-1.5 border-ink-2 rounded relative ${
              activeTab === "queue"
                ? "bg-warning text-ink shadow-brutal"
                : "bg-cream text-ink hover:bg-white"
            }`}
          >
            <UserCheck size={14} />
            <span>Approvals</span>
            {pendingApprovalsCount > 0 && (
              <span className="bg-danger text-white text-[10px] font-mono font-bold px-1.5 py-0.2 rounded-full border border-ink">
                {pendingApprovalsCount}
              </span>
            )}
          </button>

          <button
            onClick={() => setActiveTab("audit")}
            className={`btn-press px-3 py-1.5 text-xs font-heading font-bold flex items-center gap-1.5 border-ink-2 rounded ${
              activeTab === "audit"
                ? "bg-mint text-ink shadow-brutal"
                : "bg-cream text-ink hover:bg-white"
            }`}
          >
            <ShieldCheck size={14} />
            <span>Audit Chain</span>
          </button>

          <button
            onClick={() => setActiveTab("policy")}
            className={`btn-press px-3 py-1.5 text-xs font-heading font-bold flex items-center gap-1.5 border-ink-2 rounded ${
              activeTab === "policy"
                ? "bg-yellow-200 text-ink shadow-brutal"
                : "bg-cream text-ink hover:bg-white"
            }`}
          >
            <Scale size={14} />
            <span>Policy Dial</span>
          </button>

          <button
            onClick={() => setActiveTab("evals")}
            className={`btn-press px-3 py-1.5 text-xs font-heading font-bold flex items-center gap-1.5 border-ink-2 rounded ${
              activeTab === "evals"
                ? "bg-purple-200 text-ink shadow-brutal"
                : "bg-cream text-ink hover:bg-white"
            }`}
          >
            <Activity size={14} />
            <span>Evals Scoreboard</span>
          </button>

          <button
            onClick={() => setActiveTab("attacks")}
            className={`btn-press px-3 py-1.5 text-xs font-heading font-bold flex items-center gap-1.5 border-ink-2 rounded ${
              activeTab === "attacks"
                ? "bg-danger text-white shadow-brutal"
                : "bg-cream text-ink hover:bg-white"
            }`}
          >
            <ShieldAlert size={14} />
            <span>Attack Mode</span>
          </button>
        </nav>

        {/* Role Switcher */}
        <div className="flex items-center gap-2 bg-cream p-1 border-ink-2 rounded shadow-brutal-sm">
          <span className="text-[11px] font-mono font-bold px-2 text-ink-muted">ROLE:</span>
          <button
            onClick={() => setRole("customer")}
            className={`px-2.5 py-1 text-xs font-mono font-bold rounded transition-all ${
              role === "customer"
                ? "bg-ink text-white shadow-sm"
                : "text-ink hover:bg-white"
            }`}
          >
            Customer
          </button>
          <button
            onClick={() => setRole("supervisor")}
            className={`px-2.5 py-1 text-xs font-mono font-bold rounded transition-all ${
              role === "supervisor"
                ? "bg-navy text-white shadow-sm"
                : "text-ink hover:bg-white"
            }`}
          >
            Supervisor
          </button>
        </div>
      </div>
    </header>
  );
};
