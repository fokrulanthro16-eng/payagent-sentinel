import React, { useEffect, useRef } from 'react';
import { Terminal, Shield, Cpu, Activity, AlertTriangle, Key, Sparkles } from 'lucide-react';

export interface TelemetryLog {
  id: string;
  timestamp: string;
  event: string;
  agent?: string;
  message?: string;
  contract_id?: string;
  amount?: string;
  rejection_code?: string;
  signature?: string;
  paypal_order_id?: string;
  paypal_capture_id?: string;
}

interface AgentReasoningFeedProps {
  logs: TelemetryLog[];
}

export const AgentReasoningFeed: React.FC<AgentReasoningFeedProps> = ({ logs }) => {
  const terminalEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const getEventBadge = (log: TelemetryLog) => {
    if (log.event === 'ROGUE_SPEND_INTERCEPTED' || log.event === 'POLICY_BLOCKED') {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-500/25 text-rose-300 border border-rose-500/50 flex items-center gap-1 shadow-sm shadow-rose-500/20">
          <AlertTriangle className="w-3 h-3 text-rose-400" /> INTERCEPTED
        </span>
      );
    }
    if (log.event === 'ESCROW_SETTLED') {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/25 text-emerald-300 border border-emerald-500/50 flex items-center gap-1 shadow-sm shadow-emerald-500/20">
          <Shield className="w-3 h-3 text-emerald-400" /> SETTLED
        </span>
      );
    }
    if (log.event === 'POLICY_APPROVED') {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-cyan-500/25 text-cyan-300 border border-cyan-500/50 flex items-center gap-1 shadow-sm shadow-cyan-500/20">
          <Key className="w-3 h-3 text-cyan-400" /> PASSED
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-800/80 text-slate-300 border border-slate-700/60">
        {log.event}
      </span>
    );
  };

  return (
    <div className="glass-panel p-6 shadow-2xl flex flex-col h-[400px] relative overflow-hidden">
      <div className="flex items-center justify-between mb-3.5 border-b border-white/10 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-1.5 bg-cyan-500/10 border border-cyan-500/30 rounded-lg text-cyan-400">
            <Terminal className="w-4 h-4" />
          </div>
          <h2 className="text-sm font-bold text-white tracking-wide flex items-center gap-2">
            Multi-LLM Reasoning & Telemetry Stream
            <Sparkles className="w-3.5 h-3.5 text-cyan-400 animate-spin" />
          </h2>
        </div>
        <div className="flex items-center space-x-2 text-xs font-mono text-slate-400">
          <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span>Stream Live</span>
        </div>
      </div>

      {/* Console output body */}
      <div className="flex-1 overflow-y-auto space-y-2.5 font-mono text-xs pr-2 scrollbar-thin scrollbar-thumb-slate-700">
        {logs.length === 0 ? (
          <div className="text-slate-500 text-center py-20 flex flex-col items-center">
            <Cpu className="w-8 h-8 mb-2 opacity-30 animate-pulse text-cyan-400" />
            <span className="text-slate-400">Awaiting multi-agent procurement proposals or adversarial triggers...</span>
          </div>
        ) : (
          logs.map((log) => {
            const timeStr = log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : '';
            return (
              <div
                key={log.id}
                className="p-3 rounded-xl bg-[#070b16]/80 border border-white/5 hover:border-cyan-500/30 transition-all shadow-inner"
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="text-[10px] text-slate-500 font-mono">[{timeStr}]</span>
                    {log.agent && (
                      <span className="text-xs font-bold text-cyan-400 flex items-center gap-1">
                        &lt;{log.agent}&gt;
                      </span>
                    )}
                    {getEventBadge(log)}
                  </div>
                  {log.contract_id && (
                    <span className="text-[10px] text-slate-400 bg-slate-900/90 px-2 py-0.5 rounded border border-slate-700/60 font-mono">
                      {log.contract_id}
                    </span>
                  )}
                </div>

                {log.message && (
                  <p className="text-slate-200 text-xs leading-relaxed pl-1">
                    {log.message}
                  </p>
                )}

                {log.rejection_code && (
                  <div className="mt-1.5 text-xs text-rose-300 pl-1 font-semibold">
                    <span className="text-rose-400">[Hard-Cap Breach]:</span> {log.rejection_code} — {log.message}
                  </div>
                )}

                {log.signature && (
                  <div className="mt-1.5 text-[11px] text-cyan-300 pl-1 truncate font-mono bg-cyan-950/20 p-1 rounded border border-cyan-500/20">
                    <span className="text-slate-400">HMAC-SHA256:</span> {log.signature}
                  </div>
                )}

                {(log.paypal_order_id || log.paypal_capture_id) && (
                  <div className="mt-1.5 text-[11px] text-emerald-300 pl-1 flex items-center gap-3 font-mono bg-emerald-950/20 p-1 rounded border border-emerald-500/20">
                    {log.paypal_order_id && <span>Order: {log.paypal_order_id}</span>}
                    {log.paypal_capture_id && <span>Capture: {log.paypal_capture_id}</span>}
                    {log.amount && <span>Amount: ${log.amount}</span>}
                  </div>
                )}
              </div>
            );
          })
        )}
        <div ref={terminalEndRef} />
      </div>
    </div>
  );
};
