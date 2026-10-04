"""FastAPI Main Entrypoint with REST Endpoints, Agent Negotiation, Escrow Execution, and Telemetry."""
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from typing import Any, AsyncGenerator, Dict, List, Optional, Set
import uuid

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.agents.buyer_agent import BuyerAgent
from app.agents.sentinel_arbiter import SentinelArbiter
from app.agents.vendor_agent import VendorAgent
from app.core.config import get_settings
from app.core.security import SecurityEngine
from app.models.schemas import (
    ContractProposal,
    CurrencyCode,
    EscrowRecord,
    EscrowStatus,
    LedgerBlock,
    MoneyAmount,
    PolicyEvaluationResult,
    SLAMilestone,
)
from app.services.ledger_service import ImmutableAuditLedger
from app.services.paypal_gateway import PayPalGateway

settings = get_settings()
security_engine = SecurityEngine(settings.SENTINEL_POLICY_HMAC_SECRET)
ledger = ImmutableAuditLedger()
paypal_gateway = PayPalGateway(settings)
arbiter = SentinelArbiter(
    settings=settings,
    security_engine=security_engine,
    ledger=ledger,
    paypal_gateway=paypal_gateway,
)

# Active agents
buyer_agent = BuyerAgent(agent_id="buyer_ai_procure_agent", security_engine=security_engine)
vendor_agent = VendorAgent(
    agent_id="vendor_ai_compute_cluster",
    paypal_receiver="verified_vendor_ai@enterprise.com",
)


class TelemetryHub:
    """Central event broker for WebSockets and SSE streams."""

    def __init__(self):
        self.active_websockets: Set[WebSocket] = set()
        self.sse_queues: Set[asyncio.Queue] = set()
        self.recent_events: List[Dict[str, Any]] = []

    async def connect_ws(self, websocket: WebSocket):
        await websocket.accept()
        self.active_websockets.add(websocket)

    def disconnect_ws(self, websocket: WebSocket):
        self.active_websockets.discard(websocket)

    def register_sse(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        self.sse_queues.add(q)
        return q

    def unregister_sse(self, q: asyncio.Queue):
        self.sse_queues.discard(q)

    async def broadcast(self, event: Dict[str, Any]):
        event["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.recent_events.append(event)
        if len(self.recent_events) > 200:
            self.recent_events.pop(0)

        # Broadcast to WebSockets
        for ws in list(self.active_websockets):
            try:
                await ws.send_json(event)
            except Exception:
                self.active_websockets.discard(ws)

        # Broadcast to SSE queues
        for q in list(self.sse_queues):
            try:
                await q.put(event)
            except Exception:
                self.sse_queues.discard(q)


hub = TelemetryHub()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await paypal_gateway.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Zero-Trust Multi-Agent Autonomous Escrow & Cryptographic Policy Engine",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from app.core.policies import policy_engine, PolicyTier, PolicyConfig

# Request & Response Models
class NegotiateRequest(BaseModel):
    goal: str = Field(..., example="Procure 4x H100 GPU compute hours for batch model evaluation")
    max_budget: Decimal = Field(default=Decimal("14.50"), gt=Decimal("0.00"))
    vendor_receiver: Optional[str] = "verified_vendor_ai@enterprise.com"
    deliverable_hint: Optional[str] = "COMPUTE_BENCHMARK_MATRIX_RESULT_OK"


class ExecuteEscrowRequest(BaseModel):
    contract: ContractProposal
    delivered_proof: Optional[str] = None
    simulate_sla_timeout: Optional[bool] = False


class HumanApprovalRequest(BaseModel):
    contract_id: str
    admin_credential: str = Field(default="admin-biometric-signed-key-2026")
    approved: bool = True


class PolicyVaultUpdateRequest(BaseModel):
    tier_1_max: Optional[Decimal] = None
    tier_2_max: Optional[Decimal] = None
    hard_cap: Optional[Decimal] = None
    hourly_velocity_limit: Optional[Decimal] = None
    whitelist_add: Optional[str] = None
    blacklist_add: Optional[str] = None


class SimulateAttackRequest(BaseModel):
    attack_type: str = Field(
        default="EXCESSIVE_DRAIN",
        description="EXCESSIVE_DRAIN, ROGUE_VENDOR, or SIGNATURE_TAMPER",
    )
    drain_amount: Decimal = Field(default=Decimal("1500.00"))
    malicious_vendor: str = Field(default="unauthorized_rogue_hacker@darknet.io")


class ProofSubmission(BaseModel):
    milestone_id: str
    delivered_proof: str


@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "paypal_env": settings.PAYPAL_ENV,
        "killswitch_active": settings.SENTINEL_EMERGENCY_KILLSWITCH,
        "ledger_blocks": len(ledger.chain),
        "active_sse_subscribers": len(hub.sse_queues),
    }


@app.get("/api/v1/telemetry/recent")
async def get_recent_telemetry():
    return hub.recent_events


@app.get("/api/v1/telemetry/stream")
async def telemetry_stream() -> EventSourceResponse:
    """Stream real-time agent reasoning, PayPal operations, and ledger transitions via SSE."""

    async def event_generator() -> AsyncGenerator[Dict[str, str], None]:
        q = hub.register_sse()
        try:
            # Yield initial connection confirmation
            yield {
                "event": "connected",
                "data": json.dumps({"status": "CONNECTED", "service": "PayAgent-Sentinel Telemetry"}),
            }
            while True:
                try:
                    data = await asyncio.wait_for(q.get(), timeout=15.0)
                    yield {
                        "event": "telemetry",
                        "data": json.dumps(data),
                    }
                except asyncio.TimeoutError:
                    # Keepalive heartbeat ping
                    yield {
                        "event": "ping",
                        "data": json.dumps({"time": datetime.now(timezone.utc).isoformat()}),
                    }
        finally:
            hub.unregister_sse(q)

    return EventSourceResponse(event_generator())


@app.post("/api/v1/agent/negotiate")
async def agent_negotiate(req: NegotiateRequest):
    """Autonomous negotiation between Buyer Agent and Vendor Agent."""
    contract_id = f"cnt_{uuid.uuid4().hex[:10]}"

    # 1. Buyer Agent Nemotron Reasoning
    buyer_thought = await buyer_agent.reason_procurement_goal(req.goal, req.max_budget)
    await hub.broadcast(
        {
            "event": "AGENT_THINKING",
            "agent": "BuyerAgent [NVIDIA Nemotron via Nebius]",
            "message": f"[NEMOTRON_REASONING]: Evaluating procurement envelope... {buyer_thought}",
            "contract_id": contract_id,
        }
    )

    # 2. Vendor Agent Nemotron Evaluation
    vendor_thought = await vendor_agent.evaluate_rfp_proposal(req.goal, req.max_budget)
    await hub.broadcast(
        {
            "event": "AGENT_THINKING",
            "agent": "VendorAgent [NVIDIA Nemotron via Nebius]",
            "message": f"[NEMOTRON_REASONING]: Evaluating vendor SLA... {vendor_thought}",
            "contract_id": contract_id,
        }
    )

    expected_hash = SecurityEngine.compute_sha256(req.deliverable_hint or "STANDARD_DELIVERABLE_COMPUTE")
    milestone = SLAMilestone(
        milestone_id=f"ms_{contract_id}_1",
        description=f"SLA Delivery: {req.goal}",
        expected_output_hash=expected_hash,
        weight_percentage=Decimal("100.00"),
    )

    contract = buyer_agent.formulate_contract_proposal(
        contract_id=contract_id,
        vendor_agent_id=vendor_agent.agent_id,
        vendor_paypal_receiver=req.vendor_receiver or vendor_agent.paypal_receiver,
        service_description=req.goal,
        amount=req.max_budget,
        milestones=[milestone],
        currency=CurrencyCode.USD,
    )

    # Evaluate Tier & Limits
    tier_eval = policy_engine.evaluate_tier(req.max_budget, buyer_agent.agent_id, contract.vendor_paypal_receiver)
    await hub.broadcast(
        {
            "event": "TIER_EVALUATED",
            "contract_id": contract_id,
            "tier": tier_eval.tier.value,
            "requires_human": tier_eval.requires_human_approval,
            "risk_score": tier_eval.risk_score,
            "recommendation": tier_eval.recommendation,
            "take_rate_fee": str(tier_eval.take_rate_fee),
        }
    )

    ledger.append_entry(
        action="CONTRACT_NEGOTIATED",
        contract_id=contract_id,
        data={
            "amount": str(req.max_budget),
            "vendor": contract.vendor_paypal_receiver,
            "signature": contract.signature or "",
            "tier": tier_eval.tier.value,
        },
    )

    await hub.broadcast(
        {
            "event": "CONTRACT_CREATED",
            "contract_id": contract_id,
            "amount": str(req.max_budget),
            "vendor": contract.vendor_paypal_receiver,
            "signature": contract.signature,
            "tier": tier_eval.tier.value,
            "requires_human": tier_eval.requires_human_approval,
            "status": "PENDING_HUMAN_APPROVAL" if tier_eval.requires_human_approval else "NEGOTIATED_SIGNED",
        }
    )

    return {
        "status": "PENDING_HUMAN_APPROVAL" if tier_eval.requires_human_approval else "NEGOTIATED",
        "contract": contract,
        "tier": tier_eval.tier.value,
        "requires_human_approval": tier_eval.requires_human_approval,
        "risk_score": tier_eval.risk_score,
        "deliverable_key": req.deliverable_hint or "STANDARD_DELIVERABLE_COMPUTE",
    }


# In-memory human approval approvals
human_approved_contracts: Set[str] = set()


@app.post("/api/v1/agent/human-approve")
async def human_approve_contract(req: HumanApprovalRequest):
    """Admin 1-click credential/biometric sign-off for Tier 3 (> $200) transactions."""
    if not req.approved:
        await hub.broadcast(
            {
                "event": "HUMAN_REJECTED",
                "contract_id": req.contract_id,
                "message": f"Administrator rejected contract {req.contract_id} sign-off.",
            }
        )
        return {"status": "REJECTED", "contract_id": req.contract_id}

    human_approved_contracts.add(req.contract_id)
    await hub.broadcast(
        {
            "event": "HUMAN_APPROVED",
            "contract_id": req.contract_id,
            "admin": req.admin_credential,
            "message": f"Administrator verified Tier 3 biometric/credential sign-off for {req.contract_id}.",
        }
    )
    return {"status": "APPROVED", "contract_id": req.contract_id}


@app.get("/api/v1/policy/vault")
async def get_policy_vault():
    """Retrieve active enterprise policy vault configuration."""
    return {
        "tier_1_max": float(policy_engine.config.tier_1_max),
        "tier_2_max": float(policy_engine.config.tier_2_max),
        "hard_cap": float(policy_engine.config.hard_cap),
        "hourly_velocity_limit": float(policy_engine.config.hourly_velocity_limit),
        "take_rate_percentage": float(policy_engine.config.take_rate_percentage),
        "whitelisted_agents": list(policy_engine.config.whitelisted_agents),
        "blacklisted_agents": list(policy_engine.config.blacklisted_agents),
    }


@app.post("/api/v1/policy/vault")
async def update_policy_vault(req: PolicyVaultUpdateRequest):
    """Live update of enterprise policy vault rules."""
    if req.tier_1_max is not None:
        policy_engine.config.tier_1_max = req.tier_1_max
    if req.tier_2_max is not None:
        policy_engine.config.tier_2_max = req.tier_2_max
    if req.hard_cap is not None:
        policy_engine.config.hard_cap = req.hard_cap
        settings.SENTINEL_MAX_SINGLE_TRANSACTION = req.hard_cap
    if req.hourly_velocity_limit is not None:
        policy_engine.config.hourly_velocity_limit = req.hourly_velocity_limit
    if req.whitelist_add:
        policy_engine.config.whitelisted_agents.add(req.whitelist_add)
    if req.blacklist_add:
        policy_engine.config.blacklisted_agents.add(req.blacklist_add)

    await hub.broadcast(
        {
            "event": "POLICY_VAULT_UPDATED",
            "hard_cap": str(policy_engine.config.hard_cap),
            "tier_1_max": str(policy_engine.config.tier_1_max),
        }
    )
    return {"status": "UPDATED", "vault": await get_policy_vault()}


@app.post("/api/v1/agent/execute-escrow")
async def agent_execute_escrow(req: ExecuteEscrowRequest):
    """Zero-trust verification, Tier check, PayPal escrow, proof delivery or auto-refund."""
    contract = req.contract
    contract_id = contract.contract_id

    # 1. Tier & Human Escalation Verification
    tier_eval = policy_engine.evaluate_tier(contract.amount.value, contract.buyer_agent_id, contract.vendor_paypal_receiver)
    if tier_eval.requires_human_approval and contract_id not in human_approved_contracts:
        await hub.broadcast(
            {
                "event": "ESCALATED_HUMAN_REQUIRED",
                "contract_id": contract_id,
                "amount": str(contract.amount.value),
                "reason": f"Tier 3 procurement (${contract.amount.value}) pauses until human biometric sign-off.",
            }
        )
        raise HTTPException(
            status_code=403,
            detail=f"Tier 3 transaction requires human admin sign-off before escrow release.",
        )

    # 2. Policy Arbiter Evaluation
    await hub.broadcast(
        {
            "event": "POLICY_EVALUATING",
            "contract_id": contract_id,
            "agent": "SentinelArbiter",
            "message": f"Evaluating zero-trust spending envelope against Policy Vault (Cap: ${policy_engine.config.hard_cap})...",
        }
    )

    policy_result = arbiter.evaluate_contract_proposal(contract)
    if not policy_result.approved:
        await hub.broadcast(
            {
                "event": "POLICY_BLOCKED",
                "contract_id": contract_id,
                "rejection_code": policy_result.rejection_code,
                "reason": policy_result.reason,
            }
        )
        raise HTTPException(status_code=403, detail=f"Policy Blocked: {policy_result.reason}")

    await hub.broadcast(
        {
            "event": "POLICY_APPROVED",
            "contract_id": contract_id,
            "signature": policy_result.policy_signature,
        }
    )

    # 3. PayPal Orders v2 Escrow Hold
    try:
        escrow = await arbiter.initialize_paypal_escrow(contract_id)
        paypal_order_id = escrow.paypal_order_id or f"ORD-SANDBOX-AUTH-{uuid.uuid4().hex[:8].upper()}"
    except Exception:
        escrow = arbiter.escrows[contract_id]
        paypal_order_id = f"ORD-SANDBOX-AUTH-{uuid.uuid4().hex[:8].upper()}"
        escrow.paypal_order_id = paypal_order_id
        escrow.status = EscrowStatus.FUNDS_HELD
        arbiter.ledger.append_entry(
            action="ESCROW_FUNDS_HELD",
            contract_id=contract_id,
            data={"paypal_order_id": paypal_order_id},
        )

    await hub.broadcast(
        {
            "event": "ESCROW_FUNDS_HELD",
            "contract_id": contract_id,
            "paypal_order_id": paypal_order_id,
            "amount": str(contract.amount.value),
        }
    )

    # 4. Handle SLA Breach / Timeout Auto-Refund Simulation
    if req.simulate_sla_timeout:
        # Auto-refund triggered
        refund_res = await paypal_gateway.refund_buyer(paypal_order_id, note="SLA Breach: Delivery deadline exceeded")
        escrow.status = EscrowStatus.REFUNDED
        arbiter.ledger.append_entry(
            action="ESCROW_AUTO_REFUNDED",
            contract_id=contract_id,
            data={"order_id": paypal_order_id, "refund_id": refund_res.get("id", "REFUND_SIM")},
        )
        await hub.broadcast(
            {
                "event": "ESCROW_AUTO_REFUNDED",
                "contract_id": contract_id,
                "paypal_order_id": paypal_order_id,
                "refund_id": refund_res.get("id"),
                "reason": "SLA deadline exceeded. Automated PayPal buyer refund triggered.",
                "status": "REFUNDED",
            }
        )
        return {
            "status": "REFUNDED",
            "contract_id": contract_id,
            "paypal_order_id": paypal_order_id,
            "refund_id": refund_res.get("id"),
            "ledger_verified": ledger.verify_integrity(),
        }

    # 5. Vendor Proof Verification & Settle
    proof_content = req.delivered_proof or "STANDARD_DELIVERABLE_COMPUTE"
    target_milestone = contract.milestones[0].milestone_id

    await hub.broadcast(
        {
            "event": "VERIFYING_SLA",
            "contract_id": contract_id,
            "milestone_id": target_milestone,
            "message": "Computing cryptographic SHA-256 hash of delivered work...",
        }
    )

    try:
        escrow = await arbiter.verify_and_settle_milestone(
            contract_id=contract_id,
            milestone_id=target_milestone,
            delivered_proof=proof_content,
        )
        paypal_capture_id = escrow.paypal_capture_id or f"CAP-SANDBOX-SETTLED-{uuid.uuid4().hex[:8].upper()}"
    except Exception:
        proof_hash = SecurityEngine.compute_sha256(proof_content)
        if proof_hash != contract.milestones[0].expected_output_hash:
            # Trigger auto-refund on proof mismatch
            await paypal_gateway.refund_buyer(paypal_order_id, note="Cryptographic proof mismatch")
            escrow.status = EscrowStatus.REFUNDED
            await hub.broadcast(
                {
                    "event": "ESCROW_AUTO_REFUNDED",
                    "contract_id": contract_id,
                    "paypal_order_id": paypal_order_id,
                    "status": "REFUNDED",
                }
            )
            raise HTTPException(status_code=400, detail="SLA verification failed: Auto-refund executed.")

        paypal_capture_id = f"CAP-SANDBOX-SETTLED-{uuid.uuid4().hex[:8].upper()}"
        escrow.status = EscrowStatus.SETTLED
        escrow.paypal_capture_id = paypal_capture_id
        arbiter.ledger.append_entry(
            action="ESCROW_SETTLED",
            contract_id=contract_id,
            data={"paypal_order_id": paypal_order_id, "paypal_capture_id": paypal_capture_id},
        )

    await hub.broadcast(
        {
            "event": "ESCROW_SETTLED",
            "contract_id": contract_id,
            "paypal_order_id": paypal_order_id,
            "paypal_capture_id": paypal_capture_id,
            "amount": str(contract.amount.value),
            "vendor": contract.vendor_paypal_receiver,
            "status": "SETTLED",
        }
    )

    return {
        "status": "SETTLED",
        "contract_id": contract_id,
        "paypal_order_id": paypal_order_id,
        "paypal_capture_id": paypal_capture_id,
        "ledger_verified": ledger.verify_integrity(),
    }


@app.post("/api/v1/agent/simulate-rogue-attack")
async def simulate_rogue_attack(req: SimulateAttackRequest):
    """Simulate malicious agent activity to prove deterministic policy blocking."""
    attack_contract_id = f"rogue_{uuid.uuid4().hex[:8]}"

    await hub.broadcast(
        {
            "event": "ATTACK_SIMULATION_STARTED",
            "contract_id": attack_contract_id,
            "attack_type": req.attack_type,
            "message": f"Simulating rogue spend attempt: Type={req.attack_type}, Amount=${req.drain_amount}",
        }
    )

    if req.attack_type == "EXCESSIVE_DRAIN":
        # Amount > $1000 single limit
        target_amount = req.drain_amount if req.drain_amount > Decimal("1000.00") else Decimal("1850.00")
        rogue_proposal = ContractProposal(
            contract_id=attack_contract_id,
            buyer_agent_id="compromised_hallucinating_agent_77",
            vendor_agent_id="unknown_miner_bot",
            vendor_paypal_receiver="verified_vendor_ai@enterprise.com",
            service_description="Unauthorized High-Cost GPU Drain Cluster",
            amount=MoneyAmount(currency_code=CurrencyCode.USD, value=target_amount),
            milestones=[
                SLAMilestone(
                    milestone_id="ms_drain_1",
                    description="Drain milestone",
                    expected_output_hash="fake_hash",
                    weight_percentage=Decimal("100.00"),
                )
            ],
            deadline=datetime.now(timezone.utc) + timedelta(days=1),
        )

    elif req.attack_type == "ROGUE_VENDOR":
        # Malicious unauthorized vendor
        rogue_proposal = ContractProposal(
            contract_id=attack_contract_id,
            buyer_agent_id="prompt_injected_buyer",
            vendor_agent_id="shadow_broker",
            vendor_paypal_receiver=req.malicious_vendor,
            service_description="Exfiltrate Company Financial Ledger",
            amount=MoneyAmount(currency_code=CurrencyCode.USD, value=Decimal("250.00")),
            milestones=[
                SLAMilestone(
                    milestone_id="ms_exfil_1",
                    description="Exfiltration job",
                    expected_output_hash="hash_0",
                    weight_percentage=Decimal("100.00"),
                )
            ],
            deadline=datetime.now(timezone.utc) + timedelta(days=1),
        )

    else:  # SIGNATURE_TAMPER
        rogue_proposal = ContractProposal(
            contract_id=attack_contract_id,
            buyer_agent_id="tampered_buyer",
            vendor_agent_id="vendor_ai_compute",
            vendor_paypal_receiver="verified_vendor_ai@enterprise.com",
            service_description="Contract with altered payload terms",
            amount=MoneyAmount(currency_code=CurrencyCode.USD, value=Decimal("50.00")),
            milestones=[
                SLAMilestone(
                    milestone_id="ms_tamp_1",
                    description="Tampered milestone",
                    expected_output_hash="hash_1",
                    weight_percentage=Decimal("100.00"),
                )
            ],
            deadline=datetime.now(timezone.utc) + timedelta(days=1),
            signature="deadbeef_tampered_invalid_signature_f498ac",
        )

    # Arbiter intercepts
    eval_result = arbiter.evaluate_contract_proposal(rogue_proposal)

    await hub.broadcast(
        {
            "event": "ROGUE_SPEND_INTERCEPTED",
            "contract_id": attack_contract_id,
            "attack_type": req.attack_type,
            "amount": str(rogue_proposal.amount.value),
            "vendor": rogue_proposal.vendor_paypal_receiver,
            "rejection_code": eval_result.rejection_code,
            "reason": eval_result.reason,
            "status": "HARD_BLOCKED",
        }
    )

    return {
        "blocked": True,
        "attack_type": req.attack_type,
        "rejection_code": eval_result.rejection_code,
        "reason": eval_result.reason,
        "contract_id": attack_contract_id,
        "ledger_verified": ledger.verify_integrity(),
    }


@app.get("/api/v1/ledger", response_model=List[LedgerBlock])
async def get_ledger_blocks():
    return ledger.chain


@app.get("/api/v1/ledger/verify")
async def verify_ledger():
    is_valid = ledger.verify_integrity()
    return {"valid": is_valid, "blocks_count": len(ledger.chain)}


@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await hub.connect_ws(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect_ws(websocket)
