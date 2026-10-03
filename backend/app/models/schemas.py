"""Strict Pydantic v2 Models and Schemas for Policies, Escrows, and Payments."""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class EscrowStatus(str, Enum):
    INITIALIZED = "INITIALIZED"
    POLICY_APPROVED = "POLICY_APPROVED"
    POLICY_REJECTED = "POLICY_REJECTED"
    FUNDS_HELD = "FUNDS_HELD"  # PayPal Order Created / Authorized
    SLA_VERIFIED = "SLA_VERIFIED"
    SETTLED = "SETTLED"  # Captured / Paid out
    REFUNDED = "REFUNDED"
    DISPUTED = "DISPUTED"


class CurrencyCode(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    CAD = "CAD"
    AUD = "AUD"


class MoneyAmount(BaseModel):
    currency_code: CurrencyCode = CurrencyCode.USD
    value: Decimal = Field(..., gt=Decimal("0.00"), decimal_places=2)


class SLAMilestone(BaseModel):
    milestone_id: str
    description: str
    expected_output_hash: str
    weight_percentage: Decimal = Field(default=Decimal("100.00"), gt=Decimal("0.00"), le=Decimal("100.00"))
    completed: bool = False
    proof_data: Optional[Dict[str, str]] = None


class ContractProposal(BaseModel):
    contract_id: str
    buyer_agent_id: str
    vendor_agent_id: str
    vendor_paypal_receiver: str = Field(..., description="Email or PayPal payer ID for payouts")
    service_description: str
    amount: MoneyAmount
    milestones: List[SLAMilestone]
    deadline: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    signature: Optional[str] = None

    def to_signable_dict(self) -> dict:
        """Return canonical dictionary representation for HMAC signing."""
        return {
            "contract_id": self.contract_id,
            "buyer_agent_id": self.buyer_agent_id,
            "vendor_agent_id": self.vendor_agent_id,
            "vendor_paypal_receiver": self.vendor_paypal_receiver,
            "service_description": self.service_description,
            "amount_currency": self.amount.currency_code.value,
            "amount_value": str(self.amount.value),
            "milestone_ids": [m.milestone_id for m in self.milestones],
            "milestone_hashes": [m.expected_output_hash for m in self.milestones],
        }


class PolicyEvaluationResult(BaseModel):
    approved: bool
    rejection_code: Optional[str] = None
    reason: str
    contract_id: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    policy_signature: Optional[str] = None


class EscrowRecord(BaseModel):
    escrow_id: str
    contract: ContractProposal
    status: EscrowStatus = EscrowStatus.INITIALIZED
    paypal_order_id: Optional[str] = None
    paypal_capture_id: Optional[str] = None
    paypal_payout_batch_id: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class LedgerBlock(BaseModel):
    index: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action: str
    contract_id: str
    data: Dict[str, str]
    previous_hash: str
    block_hash: str
