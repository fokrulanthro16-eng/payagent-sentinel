"""End-to-end multi-agent escrow settlement test with cryptographic proof verification."""
from datetime import datetime, timedelta
from decimal import Decimal
import pytest
import httpx

from app.agents.buyer_agent import BuyerAgent
from app.agents.sentinel_arbiter import SentinelArbiter
from app.agents.vendor_agent import VendorAgent
from app.core.config import Settings
from app.core.security import SecurityEngine
from app.models.schemas import CurrencyCode, EscrowStatus, SLAMilestone
from app.services.ledger_service import ImmutableAuditLedger
from app.services.paypal_gateway import PayPalGateway


@pytest.mark.asyncio
async def test_end_to_end_agentic_escrow_settlement():
    """Full lifecycle:

    1. Buyer formulates and signs proposal
    2. Sentinel arbiter validates policies & initiates PayPal escrow
    3. Vendor completes computational job & provides proof
    4. Sentinel verifies proof hash against SLA, settles funds via PayPal Capture
    5. Hash-chained ledger validates end-to-end auditability
    """
    settings = Settings(
        SENTINEL_POLICY_HMAC_SECRET="integration-test-secret-key-32chars",
        SENTINEL_MAX_SINGLE_TRANSACTION=Decimal("1000.00"),
        SENTINEL_MAX_DAILY_VELOCITY=Decimal("5000.00"),
    )
    security = SecurityEngine(settings.SENTINEL_POLICY_HMAC_SECRET)
    ledger = ImmutableAuditLedger()

    # Mock PayPal API server
    def mock_paypal_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/oauth2/token":
            return httpx.Response(200, json={"access_token": "token_xyz", "expires_in": 3600})
        elif request.url.path == "/v2/checkout/orders":
            return httpx.Response(201, json={"id": "ORDER_ESCROW_999", "status": "CREATED"})
        elif "/capture" in request.url.path:
            return httpx.Response(201, json={"id": "CAPTURE_SETTLED_999", "status": "COMPLETED"})
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_paypal_handler)
    async with httpx.AsyncClient(transport=transport) as mock_client:
        gateway = PayPalGateway(settings=settings, client=mock_client)
        arbiter = SentinelArbiter(
            settings=settings,
            security_engine=security,
            ledger=ledger,
            paypal_gateway=gateway,
        )

        buyer = BuyerAgent(agent_id="buyer_ai_enterprise", security_engine=security)
        vendor = VendorAgent(
            agent_id="vendor_ai_compute",
            paypal_receiver="verified_vendor_ai@enterprise.com",
        )

        # 1. Buyer defines milestone and signs proposal
        expected_deliverable = "DATA_TRANSFORMATION_OUTPUT_MATRIX_FINAL"
        expected_hash = SecurityEngine.compute_sha256(expected_deliverable)

        milestone = SLAMilestone(
            milestone_id="ms_001",
            description="Process 1M records data batch",
            expected_output_hash=expected_hash,
            weight_percentage=Decimal("100.00"),
        )

        contract = buyer.formulate_contract_proposal(
            contract_id="contract_hackathon_2026",
            vendor_agent_id=vendor.agent_id,
            vendor_paypal_receiver=vendor.paypal_receiver,
            service_description="High-throughput batch inference",
            amount=Decimal("450.00"),
            milestones=[milestone],
            currency=CurrencyCode.USD,
        )

        # 2. Arbiter evaluates policy
        eval_result = arbiter.evaluate_contract_proposal(contract)
        assert eval_result.approved is True

        # Arbiter creates PayPal escrow order
        escrow = await arbiter.initialize_paypal_escrow(contract.contract_id)
        assert escrow.status == EscrowStatus.FUNDS_HELD
        assert escrow.paypal_order_id == "ORDER_ESCROW_999"

        # 3. Vendor delivers proof
        work = vendor.deliver_work(
            contract_id=contract.contract_id,
            milestone_id="ms_001",
            raw_output=expected_deliverable,
        )

        # 4. Arbiter verifies SLA proof and settles funds
        settled_escrow = await arbiter.verify_and_settle_milestone(
            contract_id=contract.contract_id,
            milestone_id="ms_001",
            delivered_proof=work["raw_output"],
        )

        assert settled_escrow.status == EscrowStatus.SETTLED
        assert settled_escrow.paypal_capture_id == "CAPTURE_SETTLED_999"

        # 5. Ledger integrity test
        assert ledger.verify_integrity() is True
        contract_entries = ledger.get_entries_for_contract(contract.contract_id)
        assert len(contract_entries) >= 3  # POLICY_APPROVED, FUNDS_HELD, SLA_VERIFIED, ESCROW_SETTLED
