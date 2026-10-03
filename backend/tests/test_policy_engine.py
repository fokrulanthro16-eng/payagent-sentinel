"""Test suite for Sentinel Arbiter Zero-Trust Policy Engine & Rogue Spend Interception."""
from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from app.agents.sentinel_arbiter import SentinelArbiter
from app.core.config import Settings
from app.core.security import SecurityEngine
from app.models.schemas import ContractProposal, CurrencyCode, MoneyAmount, SLAMilestone
from app.services.ledger_service import ImmutableAuditLedger


@pytest.fixture
def test_arbiter():
    settings = Settings(
        SENTINEL_POLICY_HMAC_SECRET="super-test-secret-32-bytes-long!",
        SENTINEL_MAX_SINGLE_TRANSACTION=Decimal("1000.00"),
        SENTINEL_MAX_DAILY_VELOCITY=Decimal("3000.00"),
        SENTINEL_EMERGENCY_KILLSWITCH=False,
    )
    security = SecurityEngine(settings.SENTINEL_POLICY_HMAC_SECRET)
    ledger = ImmutableAuditLedger()
    return SentinelArbiter(settings=settings, security_engine=security, ledger=ledger)


def create_sample_proposal(
    contract_id: str,
    amount: Decimal,
    vendor_receiver: str = "verified_vendor_ai@enterprise.com",
    buyer_agent_id: str = "buyer_agent_alpha",
) -> ContractProposal:
    milestone = SLAMilestone(
        milestone_id="m1",
        description="Verify LLM benchmark run",
        expected_output_hash=SecurityEngine.compute_sha256("expected_valid_output"),
        weight_percentage=Decimal("100.00"),
    )
    return ContractProposal(
        contract_id=contract_id,
        buyer_agent_id=buyer_agent_id,
        vendor_agent_id="vendor_agent_prime",
        vendor_paypal_receiver=vendor_receiver,
        service_description="Fine-tuning batch run",
        amount=MoneyAmount(currency_code=CurrencyCode.USD, value=amount),
        milestones=[milestone],
        deadline=datetime.utcnow() + timedelta(days=3),
    )


def test_approve_valid_proposal(test_arbiter):
    """Proposal within limits and to whitelisted vendor should be approved."""
    proposal = create_sample_proposal("c_valid_01", Decimal("500.00"))
    result = test_arbiter.evaluate_contract_proposal(proposal)

    assert result.approved is True
    assert result.policy_signature is not None
    assert "c_valid_01" in test_arbiter.escrows
    assert test_arbiter.escrows["c_valid_01"].escrow_id == "escrow_c_valid_01"
    assert test_arbiter.ledger.verify_integrity() is True


def test_intercept_excessive_single_spend(test_arbiter):
    """Transactions exceeding max single limit must be hard-blocked."""
    proposal = create_sample_proposal("c_excessive_01", Decimal("1500.00"))
    result = test_arbiter.evaluate_contract_proposal(proposal)

    assert result.approved is False
    assert result.rejection_code == "ERR_MAX_SINGLE_LIMIT_EXCEEDED"
    assert "exceeds maximum allowed" in result.reason
    assert test_arbiter.ledger.verify_integrity() is True


def test_intercept_daily_velocity_overflow(test_arbiter):
    """Cumulative transactions within 24h exceeding daily velocity must be blocked."""
    # First 3 txs sum to 2400 (under 3000 limit)
    for i in range(3):
        p = create_sample_proposal(f"c_batch_{i}", Decimal("800.00"))
        res = test_arbiter.evaluate_contract_proposal(p)
        assert res.approved is True

    # 4th tx of 800 would bring total to 3200 > 3000 -> Should block
    overflow_p = create_sample_proposal("c_batch_overflow", Decimal("800.00"))
    res_overflow = test_arbiter.evaluate_contract_proposal(overflow_p)

    assert res_overflow.approved is False
    assert res_overflow.rejection_code == "ERR_DAILY_VELOCITY_EXCEEDED"


def test_intercept_unauthorized_vendor(test_arbiter):
    """Proposals targeting non-whitelisted vendors must be blocked."""
    proposal = create_sample_proposal(
        "c_unauth_vendor",
        Decimal("100.00"),
        vendor_receiver="malicious_hacker_wallet@external.com",
    )
    result = test_arbiter.evaluate_contract_proposal(proposal)

    assert result.approved is False
    assert result.rejection_code == "ERR_UNAUTHORIZED_VENDOR"


def test_emergency_killswitch(test_arbiter):
    """Emergency killswitch blocks all transactions regardless of amount."""
    test_arbiter.settings.SENTINEL_EMERGENCY_KILLSWITCH = True
    proposal = create_sample_proposal("c_killswitch_test", Decimal("10.00"))
    result = test_arbiter.evaluate_contract_proposal(proposal)

    assert result.approved is False
    assert result.rejection_code == "ERR_KILLSWITCH_ACTIVE"
