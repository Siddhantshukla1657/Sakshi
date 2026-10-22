import React, { useState, useEffect, useRef } from "react";
import { Send, RotateCcw, HelpCircle, CheckCircle2, Clock, AlertTriangle, XCircle, ArrowRight } from "lucide-react";
import { Message, ActionChip, ReceiptData, UpiTimeline } from "../types";

interface CustomerChatProps {
  messages: Message[];
  onSendMessage: (text: string) => void;
  isLoading: boolean;
  onOpenWhy: (auditId: string) => void;
  onUndoRefund: (refundId: string) => void;
  role: "customer" | "supervisor";
}

export const CustomerChat: React.FC<CustomerChatProps> = ({
  messages,
  onSendMessage,
  isLoading,
  onOpenWhy,
  onUndoRefund,
  role
}) => {
  const [inputText, setInputText] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || isLoading) return;
    onSendMessage(inputText.trim());
    setInputText("");
  };

  return (
    <div className="flex flex-col h-full bg-white border-ink-3 rounded-lg shadow-brutal overflow-hidden">
      {/* Chat Header */}
      <div className="bg-cream border-b-[3px] border-ink p-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-mint border-2 border-ink animate-pulse" />
          <span className="font-heading font-bold text-sm text-ink">Sakshi Customer Console</span>
        </div>
        <div className="text-[11px] font-mono text-ink-muted">
          Active User: <span className="font-bold text-ink">Riya Sharma (CUST-101)</span>
        </div>
      </div>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex flex-col ${msg.sender === "user" ? "items-end" : "items-start"}`}
          >
            {/* Sender Label */}
            <span className="text-[10px] font-mono font-bold text-ink-muted mb-1 px-1">
              {msg.sender === "user" ? "You" : "Sakshi (AI Support Agent)"} • {msg.timestamp}
            </span>

            {/* Bubble */}
            <div
              className={`max-w-[85%] p-3.5 rounded-lg border-ink-2 font-body text-sm leading-relaxed ${
                msg.sender === "user"
                  ? "bg-cream text-ink shadow-brutal-sm ml-4"
                  : "bg-white text-ink shadow-brutal mr-4"
              }`}
            >
              {msg.text}

              {/* Action Chip */}
              {msg.action_chip && (
                <div className="mt-3 pt-2.5 border-t border-ink-2 flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {msg.action_chip.status === "PASSED" && (
                      <span className="bg-mint text-ink border border-ink text-xs font-mono font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                        <CheckCircle2 size={12} />
                        {msg.action_chip.text}
                      </span>
                    )}
                    {msg.action_chip.status === "NEEDS_APPROVAL" && (
                      <span className="bg-warning text-ink border border-ink text-xs font-mono font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                        <Clock size={12} />
                        {msg.action_chip.text}
                      </span>
                    )}
                    {msg.action_chip.status === "ESCALATED" && (
                      <span className="bg-purple-300 text-ink border border-ink text-xs font-mono font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                        <AlertTriangle size={12} />
                        {msg.action_chip.text}
                      </span>
                    )}
                    {msg.action_chip.status === "BLOCKED" && (
                      <span className="bg-danger text-white border border-ink text-xs font-mono font-bold px-2 py-0.5 rounded-full flex items-center gap-1 animate-shake">
                        <XCircle size={12} />
                        {msg.action_chip.text}
                      </span>
                    )}
                  </div>

                  {/* Why Button */}
                  {msg.action_chip.audit_id && (
                    <button
                      onClick={() => onOpenWhy(msg.action_chip?.audit_id || "")}
                      className="btn-press bg-yellow-100 hover:bg-yellow-200 text-ink text-xs font-heading font-bold px-2.5 py-1 rounded border border-ink flex items-center gap-1 shadow-brutal-sm"
                    >
                      <HelpCircle size={12} />
                      <span>Why?</span>
                    </button>
                  )}
                </div>
              )}

              {/* Resolution Receipt with Undo countdown */}
              {msg.receipt && (
                <ReceiptCard
                  receipt={msg.receipt}
                  onUndoRefund={onUndoRefund}
                  onOpenWhy={onOpenWhy}
                  role={role}
                />
              )}

              {/* UPI Failed-Transaction Timeline */}
              {msg.upi_timeline && (
                <UpiTimelineCard timeline={msg.upi_timeline} />
              )}
            </div>
          </div>
        ))}

        {/* Live Progress Indicator */}
        {isLoading && (
          <div className="flex flex-col items-start animate-pulse">
            <span className="text-[10px] font-mono text-ink-muted mb-1">Sakshi is inspecting live facts...</span>
            <div className="bg-cream border-ink-2 p-3 rounded-lg text-xs font-mono flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-agent animate-ping" />
              <span>Verifying order history, UPI settlement rails, and policy limits...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <form onSubmit={handleSubmit} className="p-3 bg-cream border-t-[3px] border-ink">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type in English or Hinglish (e.g. Refund ₹499 for ORD-901)..."
            disabled={isLoading}
            className="flex-1 bg-white border-ink-2 px-3.5 py-2.5 text-sm rounded font-body text-ink focus:outline-none focus:ring-2 focus:ring-agent shadow-brutal-sm"
          />
          <button
            type="submit"
            disabled={isLoading || !inputText.trim()}
            className="btn-press bg-agent hover:bg-agent-hover text-ink font-heading font-bold text-sm px-4 py-2.5 rounded border-ink-2 shadow-brutal flex items-center gap-1.5 disabled:opacity-50"
          >
            <span>Send</span>
            <Send size={15} />
          </button>
        </div>
      </form>
    </div>
  );
};

// Receipt Card Sub-Component
const ReceiptCard: React.FC<{
  receipt: ReceiptData;
  onUndoRefund: (refundId: string) => void;
  onOpenWhy: (auditId: string) => void;
  role: "customer" | "supervisor";
}> = ({ receipt, onUndoRefund, onOpenWhy, role }) => {
  const [secondsLeft, setSecondsLeft] = useState<number>(600); // 10 minutes default
  const [isUndone, setIsUndone] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setSecondsLeft((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  const handleUndo = () => {
    onUndoRefund(receipt.refund_id);
    setIsUndone(true);
  };

  return (
    <div className="mt-3 bg-cream border-ink-2 p-3.5 rounded-lg shadow-brutal-sm font-mono text-xs text-ink">
      <div className="flex items-center justify-between border-b border-ink-2 pb-2 mb-2">
        <span className="font-bold text-ink uppercase tracking-wider flex items-center gap-1">
          <CheckCircle2 size={13} className="text-mint fill-ink" />
          Official Resolution Receipt
        </span>
        <span className="bg-mint text-ink px-1.5 py-0.5 rounded text-[10px] font-bold border border-ink">
          ₹{receipt.amount} REFUNDED
        </span>
      </div>

      <div className="space-y-1 text-[11px] mb-3">
        <div className="flex justify-between">
          <span className="text-ink-muted">Refund ID:</span>
          <span className="font-bold">{receipt.refund_id}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-ink-muted">Order ID:</span>
          <span className="font-bold">{receipt.order_id}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-ink-muted">Policy Rule:</span>
          <span className="font-bold text-agent">{receipt.rule_ids}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-ink-muted">Audit Block:</span>
          <span className="font-bold underline cursor-pointer" onClick={() => onOpenWhy(receipt.audit_id)}>
            {receipt.audit_id}
          </span>
        </div>
      </div>

      {/* Undo Window Bar */}
      <div className="bg-white border border-ink p-2 rounded flex items-center justify-between gap-2">
        <div className="flex items-center gap-1.5">
          <Clock size={13} className={secondsLeft > 0 ? "text-agent" : "text-danger"} />
          <span className="text-[11px]">
            {isUndone ? (
              <span className="font-bold text-danger">Refund Undone by Supervisor</span>
            ) : secondsLeft > 0 ? (
              <>Undo grace window: <strong className="text-ink">{formatTime(secondsLeft)}</strong></>
            ) : (
              <span className="text-ink-muted">Undo window expired</span>
            )}
          </span>
        </div>

        {role === "supervisor" && !isUndone && secondsLeft > 0 && (
          <button
            onClick={handleUndo}
            className="btn-press bg-danger text-white text-[10px] font-bold px-2 py-1 rounded border border-ink shadow-brutal-sm flex items-center gap-1"
          >
            <RotateCcw size={10} />
            <span>Undo Action</span>
          </button>
        )}
      </div>
    </div>
  );
};

// UPI Timeline Sub-Component
const UpiTimelineCard: React.FC<{ timeline: UpiTimeline }> = ({ timeline }) => {
  return (
    <div className="mt-3 bg-cream border-ink-2 p-3.5 rounded-lg shadow-brutal-sm font-mono text-xs text-ink">
      <div className="flex items-center justify-between border-b border-ink-2 pb-2 mb-2.5">
        <span className="font-bold text-ink">UPI STATUS PIPELINE</span>
        <span className="font-bold text-agent">{timeline.upi_ref}</span>
      </div>

      <div className="space-y-2.5">
        {timeline.steps.map((step, idx) => (
          <div key={idx} className="flex items-start gap-2.5">
            <div className="mt-0.5">
              {step.status === "completed" && (
                <div className="w-4 h-4 rounded-full bg-mint border border-ink flex items-center justify-center text-[10px] font-bold">
                  ✓
                </div>
              )}
              {step.status === "active" && (
                <div className="w-4 h-4 rounded-full bg-agent border border-ink animate-pulse" />
              )}
              {step.status === "pending" && (
                <div className="w-4 h-4 rounded-full bg-gray-300 border border-ink" />
              )}
            </div>
            <div className="flex-1 flex items-center justify-between text-[11px]">
              <span className={step.status === "active" ? "font-bold text-agent" : ""}>
                {step.title}
              </span>
              <span className="text-ink-muted text-[10px]">{step.time}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
