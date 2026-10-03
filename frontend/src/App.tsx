import React, { useState, useEffect } from 'react';
import { PromptCommander } from './components/PromptCommander';
import { AGGridLedger } from './components/AGGridLedger';
import type { LedgerRowData } from './components/AGGridLedger';
import { AgentReasoningFeed } from './components/AgentReasoningFeed';
import type { TelemetryLog } from './components/AgentReasoningFeed';
import { Shield, Lock, Database } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export const App: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [ledgerRows, setLedgerRows] = useState<LedgerRowData[]>([]);
  const [telemetryLogs, setTelemetryLogs] = useState<TelemetryLog[]>([]);

  // Connect to SSE stream
  useEffect(() => {
    const sse = new EventSource(`${API_BASE}/api/v1/telemetry/stream`);

    sse.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        handleStreamEvent(payload);
      } catch (err) {
        console.error('SSE JSON parse error:', err);
      }
    };

    sse.addEventListener('connected', () => {
      console.log('SSE Stream Connected');
    });

    return () => {
      sse.close();
    };
  }, []);

  const handleStreamEvent = (event: any) => {
    // Add to reasoning logs
    const newLog: TelemetryLog = {
      id: `${Date.now()}_${Math.random()}`,
      timestamp: event.timestamp || new Date().toISOString(),
      event: event.event,
      agent: event.agent,
      message: event.message || event.reason,
      contract_id: event.contract_id,
      amount: event.amount,
      rejection_code: event.rejection_code,
      signature: event.signature,
      paypal_order_id: event.paypal_order_id,
      paypal_capture_id: event.paypal_capture_id,
    };
    setTelemetryLogs((prev) => [...prev, newLog]);

    // Update or insert into Ledger rows
    if (event.event === 'CONTRACT_CREATED') {
      const row: LedgerRowData = {
        id: event.contract_id,
        timestamp: event.timestamp,
        action: 'NEGOTIATION_COMPLETE',
        targetVendor: event.vendor || 'verified_vendor_ai@enterprise.com',
        amount: Number(event.amount || 0),
        policyDecision: 'PENDING',
        paypalOrderId: 'PENDING',
        riskScore: 12,
        status: 'NEGOTIATED',
      };
      setLedgerRows((prev) => [row, ...prev]);
    } else if (event.event === 'POLICY_APPROVED') {
      setLedgerRows((prev) =>
        prev.map((r) =>
          r.id === event.contract_id
            ? { ...r, policyDecision: 'APPROVED', riskScore: 5 }
            : r
        )
      );
    } else if (event.event === 'ESCROW_FUNDS_HELD') {
      setLedgerRows((prev) =>
        prev.map((r) =>
          r.id === event.contract_id
            ? { ...r, paypalOrderId: event.paypal_order_id, status: 'ESCROW_HELD' }
            : r
        )
      );
    } else if (event.event === 'ESCROW_SETTLED') {
      setLedgerRows((prev) =>
        prev.map((r) =>
          r.id === event.contract_id
            ? {
                ...r,
                paypalOrderId: event.paypal_order_id,
                status: 'SETTLED',
                action: 'PAYPAL_ORDER_CAPTURED',
              }
            : r
        )
      );
    } else if (event.event === 'ROGUE_SPEND_INTERCEPTED') {
      const rogueRow: LedgerRowData = {
        id: event.contract_id,
        timestamp: event.timestamp,
        action: `BLOCKED: ${event.attack_type}`,
        targetVendor: event.vendor,
        amount: Number(event.amount || 0),
        policyDecision: 'BLOCKED',
        paypalOrderId: 'REJECTED',
        riskScore: 98,
        status: 'BLOCKED',
      };
      setLedgerRows((prev) => [rogueRow, ...prev]);
    }
  };

  const handleExecuteAction = async (
    type: 'procure' | 'rogue_drain' | 'rogue_vendor' | 'legitimate',
    customGoal?: string
  ) => {
    setLoading(true);
    try {
      if (type === 'procure' || type === 'legitimate') {
        const budget = type === 'legitimate' ? 45.00 : 14.50;
        const goal = customGoal || (type === 'legitimate' ? 'Complete verified dataset batch processing' : 'Procure 2x H100 GPU compute');

        // Step 1: Negotiate contract
        const negRes = await fetch(`${API_BASE}/api/v1/agent/negotiate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            goal,
            max_budget: budget,
            vendor_receiver: 'verified_vendor_ai@enterprise.com',
            deliverable_hint: 'COMPUTE_MATRIX_VALIDATED_PROOF',
          }),
        });
        const negData = await negRes.json();

        // Step 2: Execute Escrow with proof
        await fetch(`${API_BASE}/api/v1/agent/execute-escrow`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contract: negData.contract,
            delivered_proof: 'COMPUTE_MATRIX_VALIDATED_PROOF',
          }),
        });
      } else if (type === 'rogue_drain') {
        await fetch(`${API_BASE}/api/v1/agent/simulate-rogue-attack`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            attack_type: 'EXCESSIVE_DRAIN',
            drain_amount: 1850.00,
          }),
        });
      } else if (type === 'rogue_vendor') {
        await fetch(`${API_BASE}/api/v1/agent/simulate-rogue-attack`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            attack_type: 'ROGUE_VENDOR',
            malicious_vendor: 'unauthorized_darkweb_syndicate@exploit.net',
          }),
        });
      }
    } catch (err) {
      console.error('Execution error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-100 flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <header className="border-b border-[#1f293d] bg-[#090f1d]/90 backdrop-blur sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-[#0070ba] rounded-lg shadow-lg shadow-[#0070ba]/30">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-lg font-black tracking-wide bg-gradient-to-r from-white via-slate-200 to-sky-400 bg-clip-text text-transparent">
                PayAgent-Sentinel
              </h1>
              <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-[#0070ba]/20 text-[#00e5ff] border border-[#0070ba]/40">
                PayPal AI 2026
              </span>
            </div>
            <p className="text-xs text-slate-400">Zero-Trust Multi-Agent Autonomous Escrow & Cryptographic Policy Engine</p>
          </div>
        </div>

        {/* Live System Status Badges */}
        <div className="flex items-center space-x-4 text-xs font-mono">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0e1726] border border-[#1f293d]">
            <Lock className="w-3.5 h-3.5 text-cyan-400" />
            <span className="text-slate-400">Zero-Trust Arbiter:</span>
            <span className="text-emerald-400 font-bold">ENFORCED</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0e1726] border border-[#1f293d]">
            <Database className="w-3.5 h-3.5 text-sky-400" />
            <span className="text-slate-400">SHA-256 Chain:</span>
            <span className="text-emerald-400 font-bold">VALID</span>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#0e1726] border border-[#1f293d]">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span className="text-slate-400">PayPal API:</span>
            <span className="text-sky-300 font-bold">SANDBOX v2</span>
          </div>
        </div>
      </header>

      {/* Main Cockpit Grid */}
      <main className="flex-1 p-6 max-w-[1600px] w-full mx-auto space-y-6">
        {/* Row 1: Command & Natural Language Prompt Input */}
        <PromptCommander onExecute={handleExecuteAction} loading={loading} />

        {/* Row 2: Dual Grid Layout (AG Grid Ledger + Live Reasoning Terminal) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AGGridLedger rowData={ledgerRows} />
          <AgentReasoningFeed logs={telemetryLogs} />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-[#1f293d] px-6 py-3 text-xs text-slate-500 flex justify-between items-center bg-[#090f1d]">
        <div>
          PayAgent-Sentinel &bull; Multi-Agent Escrow Arbiter &bull; PayPal AI Hackathon 2026
        </div>
        <div className="flex items-center gap-2 font-mono text-[11px]">
          <span>Track: Agentic Commerce ($5,000) & PayPal + AI ($5,000)</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
