import React, { useEffect, useRef } from 'react';
import { Terminal, Shield, Cpu, Activity, AlertTriangle, Key } from 'lucide-react';

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
        <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/40 flex items-center gap-1">
          <AlertTriangle className="w-3 h-3 text-rose-400" /> INTERCEPTED
        </span>
      );
    }
    if (log.event === 'ESCROW_SETTLED') {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center gap-1">
          <Shield className="w-3 h-3 text-emerald-400" /> SETTLED
        </span>
      );
    }
    if (log.event === 'POLICY_APPROVED') {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-bold bg-sky-500/20 text-sky-400 border border-sky-500/40 flex items-center gap-1">
          <Key className="w-3 h-3 text-sky-400" /> APPROVED
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[11px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
        {log.event}
      </span>
    );
  };

  return (
    <div className="bg-[#0e1726] border border-[#1f293d] rounded-xl p-5 shadow-2xl flex flex-col h-[380px]">
      <div className="flex items-center justify-between mb-3 border-b border-[#1f293d] pb-3">
        <div className="flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-[#00e5ff]" />
          <h2 className="text-sm font-bold text-white tracking-wide">
            Agent Reasoning & Cryptographic Telemetry Feed
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
          <div className="text-slate-500 text-center py-16 flex flex-col items-center">
            <Cpu className="w-8 h-8 mb-2 opacity-40 animate-pulse" />
            <span>Awaiting procurement proposals or security telemetry events...</span>
          </div>
        ) : (
          logs.map((log) => {
            const timeStr = log.timestamp ? new Date(log.timestamp).toLocaleTimeString() : '';
            return (
              <div
                key={log.id}
                className="p-2.5 rounded-lg bg-[#080c14] border border-[#1a2333] hover:border-[#273854] transition-colors"
              >
                <div className="flex items-center justify-between gap-2 mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-slate-500">[{timeStr}]</span>
                    {log.agent && (
                      <span className="text-xs font-bold text-[#00e5ff] flex items-center gap-1">
                        &lt;{log.agent}&gt;
                      </span>
                    )}
                    {getEventBadge(log)}
                  </div>
                  {log.contract_id && (
                    <span className="text-[10px] text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
                      ID: {log.contract_id}
                    </span>
                  )}
                </div>

                {log.message && (
                  <p className="text-slate-200 text-xs leading-relaxed pl-1">
                    {log.message}
                  </p>
                )}

                {log.rejection_code && (
                  <div className="mt-1 text-xs text-rose-400 pl-1">
                    <span className="font-bold">Code:</span> {log.rejection_code} — {log.message}
                  </div>
                )}

                {log.signature && (
                  <div className="mt-1 text-[11px] text-cyan-400/90 pl-1 truncate">
                    <span className="text-slate-500">HMAC-SHA256:</span> {log.signature}
                  </div>
                )}

                {(log.paypal_order_id || log.paypal_capture_id) && (
                  <div className="mt-1 text-[11px] text-emerald-400 pl-1 flex items-center gap-3">
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
