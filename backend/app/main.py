"""FastAPI Main Entrypoint with REST Endpoints and Real-time WebSocket Telemetry."""
from contextlib import asynccontextmanager
from typing import List, Set
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents.sentinel_arbiter import SentinelArbiter
from app.core.config import get_settings
from app.core.security import SecurityEngine
from app.models.schemas import (
    ContractProposal,
    EscrowRecord,
    LedgerBlock,
    PolicyEvaluationResult,
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


class ConnectionManager:
    """Manages real-time WebSocket client connections for Cockpit telemetry."""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)

    async def broadcast(self, message: dict):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                self.active_connections.discard(connection)


ws_manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await paypal_gateway.close()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Zero-Trust Multi-Agent Autonomous Escrow & Cryptographic Policy Engine",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    }


@app.post("/api/v1/policy/evaluate", response_model=PolicyEvaluationResult)
async def evaluate_proposal(proposal: ContractProposal):
    result = arbiter.evaluate_contract_proposal(proposal)
    await ws_manager.broadcast(
        {
            "event": "POLICY_EVALUATED",
            "contract_id": proposal.contract_id,
            "approved": result.approved,
            "reason": result.reason,
        }
    )
    return result


@app.post("/api/v1/escrow/{contract_id}/initialize", response_model=EscrowRecord)
async def initialize_escrow(contract_id: str):
    try:
        escrow = await arbiter.initialize_paypal_escrow(contract_id)
        await ws_manager.broadcast(
            {
                "event": "ESCROW_INITIALIZED",
                "contract_id": contract_id,
                "paypal_order_id": escrow.paypal_order_id,
                "status": escrow.status.value,
            }
        )
        return escrow
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PayPal Error: {str(exc)}")


@app.post("/api/v1/escrow/{contract_id}/verify-settle", response_model=EscrowRecord)
async def verify_and_settle(contract_id: str, submission: ProofSubmission):
    try:
        escrow = await arbiter.verify_and_settle_milestone(
            contract_id=contract_id,
            milestone_id=submission.milestone_id,
            delivered_proof=submission.delivered_proof,
        )
        await ws_manager.broadcast(
            {
                "event": "MILESTONE_SETTLED",
                "contract_id": contract_id,
                "milestone_id": submission.milestone_id,
                "status": escrow.status.value,
            }
        )
        return escrow
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Settlement Error: {str(exc)}")


@app.get("/api/v1/ledger", response_model=List[LedgerBlock])
async def get_ledger_blocks():
    return ledger.chain


@app.get("/api/v1/ledger/verify")
async def verify_ledger():
    is_valid = ledger.verify_integrity()
    return {"valid": is_valid, "blocks_count": len(ledger.chain)}


@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
