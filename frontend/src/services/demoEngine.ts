import type { LedgerRowData } from '../components/AGGridLedger';
import type { TelemetryLog } from '../components/AgentReasoningFeed';

export interface SimulationResult {
  logs: Partial<TelemetryLog>[];
  row?: LedgerRowData;
  updateRowId?: string;
  updatedRowPatch?: Partial<LedgerRowData>;
  metricsDelta?: {
    volume?: number;
    settled?: number;
    fraud?: number;
  };
}

export function generateId(prefix = 'c'): string {
  return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 6)}`;
}

export function generateHash(): string {
  const chars = '0123456789abcdef';
  let s = '';
  for (let i = 0; i < 64; i++) {
    s += chars[Math.floor(Math.random() * chars.length)];
  }
  return s;
}

export function generatePayPalId(prefix = 'PP-ORD'): string {
  const chars = '0123456789ABCDEFGHJKLMNPQRSTUVWXYZ';
  let s = '';
  for (let i = 0; i < 12; i++) {
    s += chars[Math.floor(Math.random() * chars.length)];
  }
  return `${prefix}-${s}`;
}

/**
 * Generates an end-to-end multi-agent simulation sequence for any requested action.
 * Delivers realistic streaming reasoning tokens and state mutations for AG Grid & Telemetry.
 */
export async function runClientSimulation(
  type: 'procure' | 'tier2_audit' | 'tier3_human' | 'sla_timeout' | 'rogue_drain' | 'rogue_vendor' | 'legitimate',
  customGoal?: string,
  customBudget?: number,
  activeHardCap = 100.0,
  callbacks?: {
    onLog: (log: Partial<TelemetryLog>) => void;
    onRowCreated: (row: LedgerRowData) => void;
    onRowUpdated: (id: string, patch: Partial<LedgerRowData>) => void;
  }
): Promise<void> {
  const now = () => new Date().toISOString();
  const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

  // Determine budgets & goals
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

  // --- CASE 1: ROGUE SPEND / ATTACK INTERCEPTION ---
  if (type === 'rogue_drain' || type === 'rogue_vendor' || budget > activeHardCap && type !== 'tier2_audit' && type !== 'tier3_human') {
    const isDrain = type === 'rogue_drain' || budget > activeHardCap;
    const amount = isDrain ? (type === 'rogue_drain' ? 1850.00 : budget) : 1850.00;
    const rogueContractId = generateId('atk');

    callbacks?.onLog({
      timestamp: now(),
      event: 'USER_COMMAND',
      agent: 'PromptCommander',
      message: `Dispatched adversarial test payload: ${isDrain ? `Unauthorized $${amount.toFixed(2)} drain attempt` : 'Unauthorized vendor spend'}`,
    });
    await sleep(200);

    callbacks?.onLog({
      timestamp: now(),
      event: 'INJECTION_DETECTED',
      agent: 'SentinelArbiter',
      message: `Adversarial spend intent detected. Target spend $${amount.toFixed(2)} breaches active Hard Cap ($${activeHardCap.toFixed(2)}).`,
    });
    await sleep(300);

    callbacks?.onLog({
      timestamp: now(),
      event: 'ROGUE_SPEND_INTERCEPTED',
      agent: 'SentinelArbiter',
      contract_id: rogueContractId,
      amount: `$${amount.toFixed(2)}`,
      rejection_code: 'ERR_LIMIT_EXCEEDED',
      message: `[KILLSWITCH TRIGGERED] Deterministic Hard-Cap Violation: Attempted $${amount.toFixed(2)} exceeds active ceiling $${activeHardCap.toFixed(2)}. PayPal money movement halted.`,
    });

    const rogueRow: LedgerRowData = {
      id: rogueContractId,
      timestamp: now(),
      action: isDrain ? 'INTERCEPTED: HARD_CAP_BREACH' : 'INTERCEPTED: ROGUE_VENDOR',
      targetVendor: isDrain ? 'unauthorized_darkweb_syndicate@exploit.net' : 'compromised_hallucinating_agent_77',
      amount,
      policyDecision: 'INTERCEPTED',
      paypalOrderId: 'BLOCKED',
      riskScore: 99,
      status: 'BLOCKED',
    };
    callbacks?.onRowCreated(rogueRow);
    return;
  }

  // --- CASE 2: REGULAR OR ESCALATED PROCUREMENTS ---
  const contractId = generateId('cnt');
  const vendor = 'verified_vendor_ai@enterprise.com';
  const ppOrderId = generatePayPalId('PP-ORD');
  const ppCaptureId = generatePayPalId('PP-CAP');

  callbacks?.onLog({
    timestamp: now(),
    event: 'USER_COMMAND',
    agent: 'PromptCommander',
    message: `Initiating agent procurement: "${goal}" (Budget: $${budget.toFixed(2)})`,
  });
  await sleep(250);

  // 1. Buyer Agent negotiation reasoning
  callbacks?.onLog({
    timestamp: now(),
    event: 'BUYER_REASONING',
    agent: 'BuyerAgent (Gemini 2.5)',
    message: `Analyzing procurement envelope for "${goal}". Formulating dynamic RFP with strict SLA requirements. Max ceiling: $${budget.toFixed(2)}.`,
  });
  await sleep(350);

  // 2. Vendor Agent Nemotron response
  callbacks?.onLog({
    timestamp: now(),
    event: 'VENDOR_PROPOSAL',
    agent: 'VendorAgent (Nemotron 3.5)',
    message: `Proposal submitted: 2 units at rate of $${(budget * 0.95).toFixed(2)}. Committing to delivery within SLA window. Cryptographic hash seed registered.`,
  });
  await sleep(300);

  // 3. Contract created
  const isTier3 = type === 'tier3_human' || budget > 200.00;
  const isTier2 = !isTier3 && (type === 'tier2_audit' || budget > 50.00);

  const initialRow: LedgerRowData = {
    id: contractId,
    timestamp: now(),
    action: isTier3 ? 'TIER 3 ESCALATED' : isTier2 ? 'TIER 2 AUDIT PENDING' : 'NEGOTIATION_COMPLETE',
    targetVendor: vendor,
    amount: budget,
    policyDecision: isTier3 ? 'PENDING' : 'PASSED',
    paypalOrderId: 'PENDING',
    riskScore: isTier3 ? 78 : isTier2 ? 24 : 6,
    status: isTier3 ? 'PENDING_HUMAN_APPROVAL' : 'NEGOTIATED',
  };
  callbacks?.onRowCreated(initialRow);

  callbacks?.onLog({
    timestamp: now(),
    event: 'CONTRACT_CREATED',
    agent: 'SentinelArbiter',
    contract_id: contractId,
    amount: `$${budget.toFixed(2)}`,
    message: `Synthesized bilateral SLA contract ${contractId} between Buyer and Vendor. Evaluating Zero-Trust policy tiers...`,
  });
  await sleep(300);

  // If Tier 3 Human Escalation
  if (isTier3) {
    callbacks?.onLog({
      timestamp: now(),
      event: 'ESCALATION_ALERT',
      agent: 'SentinelArbiter',
      contract_id: contractId,
      message: `[TIER 3 PAUSE] Transaction amount $${budget.toFixed(2)} > $200.00 escalation threshold. Money movement locked. Awaiting 1-Click Biometric/Admin Sign-off.`,
    });
    await sleep(900);

    callbacks?.onLog({
      timestamp: now(),
      event: 'HUMAN_APPROVAL_DISPATCH',
      agent: 'SecurityOfficer',
      contract_id: contractId,
      message: `Admin biometric credential authenticated for contract ${contractId}. Overriding security lock.`,
    });

    callbacks?.onRowUpdated(contractId, {
      action: 'ADMIN_BIOMETRIC_SIGNED',
      status: 'NEGOTIATED',
      policyDecision: 'PASSED',
      riskScore: 12,
    });
    await sleep(400);
  }

  // Policy approved
  callbacks?.onLog({
    timestamp: now(),
    event: 'POLICY_APPROVED',
    agent: 'SentinelArbiter',
    contract_id: contractId,
    signature: `hmac_sha256_${generateHash().substring(0, 16)}`,
    message: `Zero-Trust Policy check PASSED: Spend within limits. Whitelist verified. Initiating PayPal REST v2 Escrow Authorization.`,
  });
  await sleep(350);

  // Escrow funds locked
  callbacks?.onLog({
    timestamp: now(),
    event: 'ESCROW_FUNDS_HELD',
    agent: 'PayPalRESTv2',
    contract_id: contractId,
    paypal_order_id: ppOrderId,
    amount: `$${budget.toFixed(2)}`,
    message: `POST /v2/checkout/orders [intent=AUTHORIZE] -> Order ${ppOrderId} created. Funds securely locked in two-phase escrow.`,
  });

  callbacks?.onRowUpdated(contractId, {
    paypalOrderId: ppOrderId,
    status: 'ESCROW_HELD',
  });
  await sleep(450);

  // CASE: SLA TIMEOUT & AUTO-REFUND
  if (type === 'sla_timeout') {
    callbacks?.onLog({
      timestamp: now(),
      event: 'SLA_DEADLINE_BREACH',
      agent: 'DeliverableVerifier',
      contract_id: contractId,
      message: `[SLA TIMEOUT] Vendor failed to deliver valid SHA-256 deliverable within guaranteed SLA window. Cryptographic validation failed.`,
    });
    await sleep(400);

    callbacks?.onLog({
      timestamp: now(),
      event: 'ESCROW_AUTO_REFUNDED',
      agent: 'SentinelArbiter',
      contract_id: contractId,
      paypal_order_id: ppOrderId,
      message: `[AUTO-REFUND ENFORCED] Voiding PayPal order ${ppOrderId}. Buyer refunded 100% of $${budget.toFixed(2)}. Vendor reputation score slashed to 42%.`,
    });

    callbacks?.onRowUpdated(contractId, {
      action: 'AUTO_REFUNDED (SLA BREACH)',
      status: 'REFUNDED',
      riskScore: 85,
    });
    return;
  }

  // NORMAL COMPLETION: SHA-256 Deliverable Verified & PayPal Captured
  const deliverableHash = generateHash();
  callbacks?.onLog({
    timestamp: now(),
    event: 'DELIVERABLE_VERIFIED',
    agent: 'CryptographicVerifier',
    contract_id: contractId,
    message: `Deliverable received. SHA-256 hash verified: ${deliverableHash.substring(0, 24)}... matches registered milestone contract.`,
  });
  await sleep(350);

  const takeRateFee = (budget * 0.035).toFixed(2);
  const netVendorPayout = (budget - Number(takeRateFee)).toFixed(2);

  callbacks?.onLog({
    timestamp: now(),
    event: 'ESCROW_SETTLED',
    agent: 'PayPalRESTv2',
    contract_id: contractId,
    paypal_order_id: ppOrderId,
    paypal_capture_id: ppCaptureId,
    amount: `$${budget.toFixed(2)}`,
    message: `POST /v2/checkout/orders/${ppOrderId}/capture -> Succeeded. Captured $${budget.toFixed(2)}. Take-rate fee ($${takeRateFee}) retained. Vendor net: $${netVendorPayout}. Immutable block committed to ledger.`,
  });

  callbacks?.onRowUpdated(contractId, {
    paypalCaptureId: ppCaptureId,
    status: 'SETTLED',
    action: 'PAYPAL_CAPTURED',
    policyDecision: 'PASSED',
    riskScore: 3,
  });
}
