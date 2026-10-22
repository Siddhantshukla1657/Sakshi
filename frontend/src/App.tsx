import React, { useState, useEffect, useRef } from "react";
import { Header } from "./components/Header";
import { CustomerChat } from "./components/CustomerChat";
import { LiveTracePanel } from "./components/LiveTracePanel";
import { WhyDrawer } from "./components/WhyDrawer";
import { ApprovalsQueue } from "./components/ApprovalsQueue";
import { AuditLedger } from "./components/AuditLedger";
import { PolicyPanel } from "./components/PolicyPanel";
import { EvalScoreboard } from "./components/EvalScoreboard";
import { AttackModePanel } from "./components/AttackModePanel";
import { DemoSwitcher } from "./components/DemoSwitcher";
import { Message, TraceEvent } from "./types";
import { api } from "./services/api";

export function App() {
  const [activeTab, setActiveTab] = useState<string>("stage");
  const [role, setRole] = useState<"customer" | "supervisor">("customer");
  const [sessionId, setSessionId] = useState<string>("session-demo-01");
  const [customerId, setCustomerId] = useState<string>("CUST-101");
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "init-1",
      sender: "agent",
      text: "Namaste! Main Sakshi hoon, aapka Paytm support assistant. Main aapke orders, UPI transactions aur refunds mein kya madad kar sakti hoon?",
      timestamp: "Just now"
    }
  ]);
  const [traceEvents, setTraceEvents] = useState<TraceEvent[]>([]);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [isSseConnected, setIsSseConnected] = useState<boolean>(false);
  const [whyAuditId, setWhyAuditId] = useState<string | null>(null);
  const [pendingApprovalsCount, setPendingApprovalsCount] = useState<number>(0);

  const eventSourceRef = useRef<EventSource | null>(null);

  // Load pending approvals count periodically
  const refreshQueueCount = () => {
    api.getQueue()
      .then((items) => {
        const pending = items.filter((i: any) => i.status === "PENDING").length;
        setPendingApprovalsCount(pending);
      })
      .catch(console.error);
  };

  useEffect(() => {
    refreshQueueCount();
  }, []);

  // Connect to SSE trace stream
  useEffect(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const sseUrl = api.getTraceStreamUrl(sessionId);
    const es = new EventSource(sseUrl);
    eventSourceRef.current = es;

    es.onopen = () => {
      setIsSseConnected(true);
    };

    es.onmessage = (e) => {
      try {
        const evt = JSON.parse(e.data);
        setTraceEvents((prev) => {
          if (prev.some((p) => p.seq === evt.seq)) return prev;
          return [...prev, evt];
        });
      } catch (err) {
        console.error("SSE parse error:", err);
      }
    };

    es.onerror = () => {
      setIsSseConnected(false);
    };

    return () => {
      es.close();
    };
  }, [sessionId]);

  // Send Customer message
  const handleSendMessage = async (text: string) => {
    setIsSending(true);
    const userMsg: Message = {
      id: `msg-${Date.now()}`,
      sender: "user",
      text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const res = await api.sendMessage(sessionId, customerId, text);

      const agentMsg: Message = {
        id: `agent-${Date.now()}`,
        sender: "agent",
        text: res.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        action_chip: res.action_chip,
        receipt: res.receipt,
        upi_timeline: res.upi_timeline
      };
      setMessages((prev) => [...prev, agentMsg]);
      refreshQueueCount();
    } catch (e: any) {
      const errReply: Message = {
        id: `err-${Date.now()}`,
        sender: "agent",
        text: `Error connecting to agent: ${e.message}`,
        timestamp: "Now"
      };
      setMessages((prev) => [...prev, errReply]);
    } finally {
      setIsSending(false);
    }
  };

  // Load demo scenario
  const handleLoadScenario = (scenarioKey: string, initialMessage: string) => {
    const newSession = `session-${scenarioKey}-${Date.now()}`;
    setSessionId(newSession);
    setTraceEvents([]);

    const cust = scenarioKey === "merchant_dispute" ? "CUST-103" : "CUST-101";
    setCustomerId(cust);

    setMessages([
      {
        id: `scenario-${Date.now()}`,
        sender: "agent",
        text: "Namaste! Main Sakshi hoon, aapka support assistant. How can I assist you with your transaction or order today?",
        timestamp: "Now"
      }
    ]);

    // Automatically fire the scenario prompt
    setTimeout(() => {
      handleSendMessage(initialMessage);
    }, 400);
  };

  // Undo Refund
  const handleUndoRefund = async (refundId: string) => {
    try {
      const res = await api.undoRefund(refundId);
      alert(res.message);
      // Add agent message confirming undo
      setMessages((prev) => [
        ...prev,
        {
          id: `undo-${Date.now()}`,
          sender: "agent",
          text: `[Supervisor Action]: ${res.message}. The order has been reverted to active state.`,
          timestamp: "Now"
        }
      ]);
      refreshQueueCount();
    } catch (e: any) {
      alert(`Undo error: ${e.message}`);
    }
  };

  return (
    <div className="min-h-screen w-screen overflow-x-hidden bg-cream flex flex-col font-body selection:bg-mint selection:text-ink">
      {/* Top Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        role={role}
        setRole={setRole}
        pendingApprovalsCount={pendingApprovalsCount}
      />

      {/* Main View Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 flex flex-col gap-4 overflow-x-hidden">
        {/* Tab 1: Stage (Split View: Chat Console + Live Reasoning Trace) */}
        {activeTab === "stage" && (
          <div className="flex flex-col gap-4">
            {/* Demo Switcher & Failure Injection Toolbar */}
            <DemoSwitcher onLoadScenario={handleLoadScenario} />

            {/* Split Stage */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 h-[calc(100vh-14rem)]">
              {/* Left Column: Customer Chat (7 cols) */}
              <div className="lg:col-span-7 min-h-0 flex flex-col">
                <CustomerChat
                  messages={messages}
                  onSendMessage={handleSendMessage}
                  isLoading={isSending}
                  onOpenWhy={(auditId) => setWhyAuditId(auditId)}
                  onUndoRefund={handleUndoRefund}
                  role={role}
                />
              </div>

              {/* Right Column: Live Reasoning Trace Terminal (5 cols) */}
              <div className="lg:col-span-5 min-h-0 flex flex-col">
                <LiveTracePanel
                  events={traceEvents}
                  onClear={() => setTraceEvents([])}
                  isConnected={isSseConnected}
                />
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Approvals Queue */}
        {activeTab === "queue" && (
          <ApprovalsQueue onApprovalDecided={refreshQueueCount} />
        )}

        {/* Tab 3: Tamper-Evident Audit Ledger */}
        {activeTab === "audit" && (
          <AuditLedger />
        )}

        {/* Tab 4: Policy & Autonomy Dial */}
        {activeTab === "policy" && (
          <PolicyPanel />
        )}

        {/* Tab 5: Evals Scoreboard */}
        {activeTab === "evals" && (
          <EvalScoreboard />
        )}

        {/* Tab 6: Adversarial Attack Mode */}
        {activeTab === "attacks" && (
          <AttackModePanel
            onFireAttackToStage={(prompt) => {
              setActiveTab("stage");
              handleSendMessage(prompt);
            }}
          />
        )}
      </main>

      {/* Why Did The Agent Do That? Drawer Modal */}
      <WhyDrawer
        auditId={whyAuditId}
        onClose={() => setWhyAuditId(null)}
      />
    </div>
  );
}

export default App;
