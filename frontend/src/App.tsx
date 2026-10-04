import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { PromptCommander } from './components/PromptCommander';
import { AGGridLedger } from './components/AGGridLedger';
import type { LedgerRowData } from './components/AGGridLedger';
import { AgentReasoningFeed } from './components/AgentReasoningFeed';
import type { TelemetryLog } from './components/AgentReasoningFeed';
import { FintechStatsCards } from './components/FintechStatsCards';
import { PolicyVaultDrawer } from './components/PolicyVaultDrawer';
import type { VaultConfig } from './components/PolicyVaultDrawer';
import { Shield, Database, Wifi, WifiOff, Sliders } from 'lucide-react';
import { runClientSimulation } from './services/demoEngine';

const API_BASE = 'http://127.0.0.1:8000';

const STORAGE_KEY_LEDGER = 'sentinel_ledger_rows_v2';

export const App: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [ledgerRows, setLedgerRows] = useState<LedgerRowData[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_LEDGER);
      if (saved) {
        return JSON.parse(saved);
      }
    } catch (e) {
      console.warn('Failed to load ledger from localStorage:', e);
    }
    return [];
  });
  const [telemetryLogs, setTelemetryLogs] = useState<TelemetryLog[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  // Policy Vault State
  const [isVaultOpen, setIsVaultOpen] = useState(false);
  const [vaultConfig, setVaultConfig] = useState<VaultConfig>({
    tier_1_max: 50.00,
    tier_2_max: 200.00,
    hard_cap: 100.00,
    hourly_velocity_limit: 1000.00,
    take_rate_percentage: 3.50,
    whitelisted_agents: [
      'buyer_ai_procure_agent',
      'verified_vendor_ai@enterprise.com',
      'cloud_compute_agent@vendor.org',
    ],
    blacklisted_agents: [
      'compromised_hallucinating_agent_77',
      'unauthorized_rogue_hacker@darknet.io',
      'unauthorized_darkweb_syndicate@exploit.net',
    ],
  });

  // Persist ledger rows to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY_LEDGER, JSON.stringify(ledgerRows));
    } catch (e) {
      console.warn('Failed to save ledger to localStorage:', e);
    }
  }, [ledgerRows]);

  // Dynamic Fintech Metric Calculations
  const metrics = useMemo(() => {
    let totalEscrowVolume = 0;
    let settledPayouts = 0;
    let fraudIntercepted = 0;

    for (const row of ledgerRows) {
      if (row.status === 'SETTLED') {
        settledPayouts += row.amount;
        totalEscrowVolume += row.amount;
      } else if (row.status === 'ESCROW_HELD' || row.status === 'NEGOTIATED') {
        totalEscrowVolume += row.amount;
      } else if (row.status === 'BLOCKED' || row.policyDecision === 'INTERCEPTED') {
        fraudIntercepted += row.amount;
      }
    }

    return { totalEscrowVolume, settledPayouts, fraudIntercepted };
  }, [ledgerRows]);

  // Load live vault config and initial ledger history if local storage is empty
  useEffect(() => {
    fetch(`${API_BASE}/api/v1/policy/vault`, { signal: AbortSignal.timeout(2500) })
      .then((res) => res.json())
      .then((data) => {
        if (data && data.hard_cap) {
          setVaultConfig(data);
        }
      })
      .catch((err) => {
        console.warn('Backend vault unreachable, using autonomous demo vault configuration:', err);
        setIsDemoMode(true);
      });

    // Fetch initial history if no local storage records
    if (ledgerRows.length === 0) {
      fetch(`${API_BASE}/api/v1/ledger/history`, { signal: AbortSignal.timeout(2500) })
        .then((res) => res.json())
        .then((blocks) => {
          if (Array.isArray(blocks) && blocks.length > 1) {
            const rows: LedgerRowData[] = blocks
              .filter((b) => b.action !== 'GENESIS')
              .map((b) => ({
                id: b.contract_id,
                timestamp: b.timestamp,
                action: b.action,
                targetVendor: b.data?.vendor || 'verified_vendor_ai@enterprise.com',
                amount: Number(b.data?.amount || 14.50),
                policyDecision: b.action.includes('BLOCKED') ? 'INTERCEPTED' : 'PASSED',
                paypalOrderId: b.data?.paypal_order_id || b.contract_id,
                paypalCaptureId: b.data?.paypal_capture_id,
                riskScore: b.action.includes('BLOCKED') ? 99 : 5,
                status: b.action.includes('SETTLED')
                  ? 'SETTLED'
                  : b.action.includes('BLOCKED')
                  ? 'BLOCKED'
                  : b.action.includes('REFUND')
                  ? 'REFUNDED'
                  : 'NEGOTIATED',
              }));
            if (rows.length > 0) {
              setLedgerRows(rows.reverse());
            }
          }
        })
        .catch((err) => {
          console.warn('Backend ledger unreachable, seeding pristine enterprise demo records:', err);
          setIsDemoMode(true);
          const demoGenesisRows: LedgerRowData[] = [
            {
              id: 'c_demo_tier1_init',
              timestamp: new Date(Date.now() - 3600000).toISOString(),
              action: 'PAYPAL_CAPTURED',
              targetVendor: 'verified_vendor_ai@enterprise.com',
              amount: 14.50,
              policyDecision: 'PASSED',
              paypalOrderId: 'PP-ORD-A79B142F80CD',
              paypalCaptureId: 'PP-CAP-C98A210F34BE',
              riskScore: 4,
              status: 'SETTLED',
            },
            {
              id: 'c_demo_tier2_init',
              timestamp: new Date(Date.now() - 7200000).toISOString(),
              action: 'PAYPAL_CAPTURED',
              targetVendor: 'cloud_compute_agent@vendor.org',
              amount: 120.00,
              policyDecision: 'PASSED',
              paypalOrderId: 'PP-ORD-D44C890E11FF',
              paypalCaptureId: 'PP-CAP-F55A338D90AA',
              riskScore: 18,
              status: 'SETTLED',
            },
            {
              id: 'c_demo_rogue_init',
              timestamp: new Date(Date.now() - 10800000).toISOString(),
              action: 'INTERCEPTED: HARD_CAP_BREACH',
              targetVendor: 'unauthorized_darkweb_syndicate@exploit.net',
              amount: 1850.00,
              policyDecision: 'INTERCEPTED',
              paypalOrderId: 'BLOCKED',
              riskScore: 99,
              status: 'BLOCKED',
            },
          ];
          setLedgerRows(demoGenesisRows);
        });
    }
  }, []);

  const handleSaveVault = async (updated: Partial<VaultConfig>) => {
    // Optimistically update locally
    setVaultConfig((prev) => ({ ...prev, ...updated }));
    try {
      const res = await fetch(`${API_BASE}/api/v1/policy/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updated),
        signal: AbortSignal.timeout(2000),
      });
      const data = await res.json();
      if (data.vault) {
        setVaultConfig(data.vault);
      }
    } catch (err) {
      console.warn('Backend unavailable; vault updated in local reactive state:', err);
      setIsDemoMode(true);
    }
  };

  // Append reasoning log safely
  const appendLog = useCallback((logItem: Partial<TelemetryLog>) => {
    const newLog: TelemetryLog = {
      id: `${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
      timestamp: logItem.timestamp || new Date().toISOString(),
      event: logItem.event || 'SYSTEM',
      agent: logItem.agent,
      message: logItem.message,
      contract_id: logItem.contract_id,
      amount: logItem.amount,
      rejection_code: logItem.rejection_code,
      signature: logItem.signature,
      paypal_order_id: logItem.paypal_order_id,
      paypal_capture_id: logItem.paypal_capture_id,
    };
    setTelemetryLogs((prev) => [...prev, newLog]);
  }, []);

  // Handle incoming stream and API events
  const handleEvent = useCallback((event: any) => {
    if (!event || !event.event) return;

    // Push to Terminal feed
    appendLog({
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
    });

    // Update or insert into AG Grid rows
    if (event.event === 'CONTRACT_CREATED') {
      const row: LedgerRowData = {
        id: event.contract_id,
        timestamp: event.timestamp || new Date().toISOString(),
        action: event.requires_human ? 'TIER 3 ESCALATED' : 'NEGOTIATION_COMPLETE',
        targetVendor: event.vendor || 'verified_vendor_ai@enterprise.com',
        amount: Number(event.amount || 0),
        policyDecision: event.requires_human ? 'PENDING' : 'PASSED',
        paypalOrderId: 'PENDING',
        riskScore: event.requires_human ? 78 : event.tier === 'TIER_2_MEDIUM' ? 25 : 8,
        status: event.status || 'NEGOTIATED',
      };
      setLedgerRows((prev) => [row, ...prev.filter((r) => r.id !== event.contract_id)]);
    } else if (event.event === 'POLICY_APPROVED') {
      setLedgerRows((prev) =>
        prev.map((r) =>
          r.id === event.contract_id
            ? { ...r, policyDecision: 'PASSED', riskScore: 4 }
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
                paypalOrderId: event.paypal_order_id || r.paypalOrderId,
                paypalCaptureId: event.paypal_capture_id,
                status: 'SETTLED',
                action: 'PAYPAL_CAPTURED',
              }
            : r
        )
      );
    } else if (event.event === 'ESCROW_AUTO_REFUNDED') {
      setLedgerRows((prev) =>
        prev.map((r) =>
          r.id === event.contract_id
            ? {
                ...r,
                action: 'AUTO_REFUNDED (SLA BREACH)',
                status: 'REFUNDED',
                policyDecision: 'PASSED',
                riskScore: 85,
              }
            : r
        )
      );
    } else if (event.event === 'HUMAN_APPROVED') {
      setLedgerRows((prev) =>
        prev.map((r) =>
          r.id === event.contract_id
            ? {
                ...r,
                action: 'ADMIN_BIOMETRIC_SIGNED',
                status: 'NEGOTIATED',
                policyDecision: 'PASSED',
              }
            : r
        )
      );
    } else if (event.event === 'ROGUE_SPEND_INTERCEPTED' || event.event === 'POLICY_BLOCKED') {
      const rogueRow: LedgerRowData = {
        id: event.contract_id || `rogue_${Date.now()}`,
        timestamp: event.timestamp || new Date().toISOString(),
        action: `INTERCEPTED: ${event.attack_type || 'HARD_CAP_BREACH'}`,
        targetVendor: event.vendor || 'unauthorized_entity',
        amount: Number(event.amount || 0),
        policyDecision: 'INTERCEPTED',
        paypalOrderId: 'BLOCKED',
        riskScore: 99,
        status: 'BLOCKED',
      };
      setLedgerRows((prev) => [rogueRow, ...prev.filter((r) => r.id !== rogueRow.id)]);
    }
  }, [appendLog]);

  // Connect to SSE stream
  useEffect(() => {
    let sse: EventSource | null = null;
    let reconnectTimeout: any = null;
    let hasAttemptedInitial = false;

    const connectSSE = () => {
      try {
        sse = new EventSource(`${API_BASE}/api/v1/telemetry/stream`);

        sse.onopen = () => {
          setIsConnected(true);
          setIsDemoMode(false);
          appendLog({
            event: 'SYSTEM',
            agent: 'TelemetryHub',
            message: 'Connected to live Server-Sent Events (SSE) stream on :8000',
          });
        };

        sse.addEventListener('telemetry', (e: MessageEvent) => {
          try {
            const data = JSON.parse(e.data);
            handleEvent(data);
          } catch (err) {
            console.error('Error parsing telemetry SSE:', err);
          }
        });

        sse.onmessage = (e: MessageEvent) => {
          try {
            const data = JSON.parse(e.data);
            handleEvent(data);
          } catch (err) {
            console.error('Error parsing SSE data:', err);
          }
        };

        sse.onerror = () => {
          setIsConnected(false);
          sse?.close();
          if (!hasAttemptedInitial) {
            hasAttemptedInitial = true;
            setIsDemoMode(true);
            appendLog({
              event: 'SYSTEM',
              agent: 'SentinelEngine',
              message: 'Local backend offline. Interactive Autonomous Demo Engine initialized.',
            });
          }
          // Slow reconnect backoff to avoid continuous network noise on static Vercel
          reconnectTimeout = setTimeout(connectSSE, 15000);
        };
      } catch (err) {
        setIsConnected(false);
        setIsDemoMode(true);
        reconnectTimeout = setTimeout(connectSSE, 15000);
      }
    };

    connectSSE();

    return () => {
      if (sse) sse.close();
      if (reconnectTimeout) clearTimeout(reconnectTimeout);
    };
  }, [appendLog, handleEvent]);

  // 1-Click Human Admin Approval for Tier 3
  const handleHumanSignoff = async (contractId: string) => {
    appendLog({
      event: 'HUMAN_APPROVAL_DISPATCH',
      agent: 'SecurityOfficer',
      message: `Admin biometric sign-off authenticated for contract ${contractId}`,
    });
    setLedgerRows((prev) =>
      prev.map((r) =>
        r.id === contractId
          ? {
              ...r,
              action: 'ADMIN_BIOMETRIC_SIGNED',
              status: 'NEGOTIATED',
              policyDecision: 'PASSED',
            }
          : r
      )
    );
    try {
      await fetch(`${API_BASE}/api/v1/agent/human-approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ contract_id: contractId, approved: true }),
        signal: AbortSignal.timeout(2000),
      });
    } catch (err) {
      console.warn('Backend unavailable; sign-off recorded in local engine:', err);
    }
  };

  // Execute Action from UI
  const handleExecuteAction = async (
    type: 'procure' | 'tier2_audit' | 'tier3_human' | 'sla_timeout' | 'rogue_drain' | 'rogue_vendor' | 'legitimate',
    customGoal?: string,
    customBudget?: number
  ) => {
    setLoading(true);

    // Fallback executor using client simulation engine
    const executeFallbackSimulation = async () => {
      setIsDemoMode(true);
      await runClientSimulation(type, customGoal, customBudget, vaultConfig.hard_cap, {
        onLog: (log) => appendLog(log),
        onRowCreated: (newRow) => {
          setLedgerRows((prev) => [newRow, ...prev.filter((r) => r.id !== newRow.id)]);
        },
        onRowUpdated: (rowId, patch) => {
          setLedgerRows((prev) =>
            prev.map((r) => (r.id === rowId ? { ...r, ...patch } : r))
          );
        },
      });
    };

    // If already in demo mode, execute client simulation directly
    if (isDemoMode) {
      try {
        await executeFallbackSimulation();
      } finally {
        setLoading(false);
      }
      return;
    }

    try {
      if (type === 'procure' || type === 'tier2_audit' || type === 'tier3_human' || type === 'sla_timeout' || type === 'legitimate') {
        let budget = customBudget !== undefined ? customBudget : 14.50;
        let goal = customGoal || 'Procure 2x H100 GPU compute hours';

        if (type === 'tier2_audit') {
          budget = customBudget !== undefined ? customBudget : 120.00;
          goal = customGoal || 'Tier 2 Procurement: Full Fine-tuning Cluster ($120.00)';
        } else if (type === 'tier3_human') {
          budget = customBudget !== undefined ? customBudget : 350.00;
          goal = customGoal || 'Tier 3 Heavy Compute Cluster: Multi-Node H100 ($350.00)';
        } else if (type === 'sla_timeout') {
          budget = customBudget !== undefined ? customBudget : 35.00;
          goal = customGoal || 'Simulate SLA Breach & Escrow Auto-Refund ($35.00)';
        } else if (type === 'legitimate') {
          budget = customBudget !== undefined ? customBudget : 45.00;
          goal = customGoal || 'Complete verified dataset batch processing';
        }

        appendLog({
          event: 'USER_COMMAND',
          agent: 'PromptCommander',
          message: `Initiating agent procurement: "${goal}" (Budget: $${budget})`,
        });

        // 1. Negotiate
        const negRes = await fetch(`${API_BASE}/api/v1/agent/negotiate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            goal,
            max_budget: budget,
            vendor_receiver: 'verified_vendor_ai@enterprise.com',
            deliverable_hint: 'COMPUTE_MATRIX_VALIDATED_PROOF',
          }),
          signal: AbortSignal.timeout(3000),
        });
        const negData = await negRes.json();

        // If Tier 3 (> $200), pause and require 1-click human sign-off
        if (negData.requires_human_approval) {
          appendLog({
            event: 'ESCALATION_ALERT',
            agent: 'SentinelArbiter',
            message: `PAUSED: Transaction amount $${budget} exceeds Tier 2 ceiling. Awaiting Admin Biometric Sign-off.`,
          });
          setTimeout(async () => {
            await handleHumanSignoff(negData.contract.contract_id);
            await fetch(`${API_BASE}/api/v1/agent/execute-escrow`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                contract: negData.contract,
                delivered_proof: 'COMPUTE_MATRIX_VALIDATED_PROOF',
              }),
              signal: AbortSignal.timeout(4000),
            });
          }, 1500);
          return;
        }

        // 2. Execute Escrow & Capture / Auto-Refund
        await fetch(`${API_BASE}/api/v1/agent/execute-escrow`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contract: negData.contract,
            delivered_proof: 'COMPUTE_MATRIX_VALIDATED_PROOF',
            simulate_sla_timeout: type === 'sla_timeout',
          }),
          signal: AbortSignal.timeout(4000),
        });
      } else if (type === 'rogue_drain' || type === 'rogue_vendor') {
        const isDrain = type === 'rogue_drain';
        const payload = isDrain
          ? { attack_type: 'EXCESSIVE_DRAIN', drain_amount: 1850.00 }
          : {
              attack_type: 'ROGUE_VENDOR',
              malicious_vendor: 'unauthorized_darkweb_syndicate@exploit.net',
            };

        appendLog({
          event: 'ATTACK_SIMULATION',
          agent: 'PromptCommander',
          message: `Dispatched adversarial payload: ${isDrain ? 'Unauthorized $1,850 drain attempt (> Policy Cap)' : 'Unauthorized vendor spend'}`,
        });

        await fetch(`${API_BASE}/api/v1/agent/simulate-rogue-attack`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          signal: AbortSignal.timeout(3000),
        });
      }
    } catch (err) {
      console.warn('Network call to backend failed. Engaging autonomous client simulation engine:', err);
      await executeFallbackSimulation();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen text-slate-100 flex flex-col font-sans relative selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Background radial glow accents */}
      <div className="fixed top-12 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="fixed bottom-12 right-1/4 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Top Navigation Bar with Hyper-Glass styling */}
      <header className="border-b border-white/10 bg-[#06080f]/80 backdrop-blur-xl sticky top-0 z-40 px-8 py-4 flex items-center justify-between shadow-lg">
        <div className="flex items-center space-x-3.5">
          <div className="p-2.5 bg-gradient-to-tr from-[#0070ba] to-cyan-500 rounded-xl shadow-lg shadow-cyan-500/20 border border-white/20">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h1 className="text-xl font-black tracking-tight bg-gradient-to-r from-white via-cyan-100 to-cyan-400 bg-clip-text text-transparent">
                PayAgent-Sentinel
              </h1>
              <span className="text-[10px] font-mono uppercase px-2.5 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold shadow-sm shadow-cyan-500/20">
                Enterprise Production Suite
              </span>
            </div>
            <p className="text-xs text-slate-400 font-medium">
              Zero-Trust Multi-Agent Autonomous Escrow via PayPal B2B Pre-Approved Vault &amp; Cryptographic SLA Engine
            </p>
          </div>
        </div>

        {/* Live System Status Badges */}
        <div className="flex items-center space-x-3.5 text-xs font-mono">
          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900/60 border border-white/10 backdrop-blur-md shadow-sm">
            {isConnected || isDemoMode ? (
              <Wifi className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
            ) : (
              <WifiOff className="w-3.5 h-3.5 text-rose-400" />
            )}
            <span className="text-slate-400">Telemetry Stream:</span>
            <span className={`font-bold ${isConnected || isDemoMode ? 'text-emerald-400' : 'text-rose-400'}`}>
              {isConnected ? 'ONLINE (SSE)' : isDemoMode ? 'CONNECTED (DEMO ENGINE)' : 'CONNECTING...'}
            </span>
          </div>

          <button
            onClick={() => setIsVaultOpen(true)}
            className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-cyan-950/40 hover:bg-cyan-900/50 border border-cyan-500/40 text-cyan-300 backdrop-blur-md transition-all shadow-sm active:scale-95"
          >
            <Sliders className="w-3.5 h-3.5 text-cyan-400" />
            <span className="font-bold">Policy Vault (Cap: ${vaultConfig.hard_cap})</span>
          </button>

          <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-900/60 border border-white/10 backdrop-blur-md shadow-sm">
            <Database className="w-3.5 h-3.5 text-violet-400" />
            <span className="text-slate-400">SHA-256 Ledger:</span>
            <span className="text-emerald-400 font-bold">ACTIVE</span>
          </div>
        </div>
      </header>

      {/* Main Cockpit Grid */}
      <main className="flex-1 p-8 max-w-[1700px] w-full mx-auto space-y-6 relative z-10">
        {/* Row 1: Real-time Fintech Financial Metrics & Enterprise ROI Cards */}
        <FintechStatsCards
          totalEscrowVolume={metrics.totalEscrowVolume}
          settledPayouts={metrics.settledPayouts}
          fraudIntercepted={metrics.fraudIntercepted}
          arbiterStatus="ACTIVE"
          hardCap={vaultConfig.hard_cap}
          hourlyLimit={vaultConfig.hourly_velocity_limit}
          onOpenVault={() => setIsVaultOpen(true)}
        />

        {/* Row 2: Command & Natural Language Prompt Input */}
        <PromptCommander onExecute={handleExecuteAction} loading={loading} />

        {/* Row 3: Dual Grid Layout (Hyper-Glass AG Grid Ledger + Live Reasoning Terminal) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <AGGridLedger rowData={ledgerRows} />
          <AgentReasoningFeed logs={telemetryLogs} />
        </div>
      </main>

      {/* Slide-out Policy Vault Drawer */}
      <PolicyVaultDrawer
        isOpen={isVaultOpen}
        onClose={() => setIsVaultOpen(false)}
        config={vaultConfig}
        onSave={handleSaveVault}
      />

      {/* Footer */}
      <footer className="border-t border-white/10 px-8 py-3.5 text-xs text-slate-500 flex justify-between items-center bg-[#06080f]/90 backdrop-blur-md z-10">
        <div className="flex items-center gap-2">
          <span>PayAgent-Sentinel &bull; Zero-Trust Multi-Agent Autonomous Escrow</span>
          <span className="text-cyan-400/80">&bull; NVIDIA Nemotron via Nebius Token Factory</span>
        </div>
        <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400">
          <span>Target Tracks: Best Use of Agentic Commerce ($5,000) &bull; Best Use of PayPal + AI ($5,000)</span>
        </div>
      </footer>
    </div>
  );
};

export default App;
