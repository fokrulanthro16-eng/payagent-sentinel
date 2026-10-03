"""Sentinel Arbiter: Zero-Trust Policy Verifier and Rogue Spend Interceptor."""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Set
from app.core.config import Settings, get_settings
from app.core.security import SecurityEngine
from app.models.schemas import (
    ContractProposal,
    EscrowRecord,
    EscrowStatus,
    PolicyEvaluationResult,
    SLAMilestone,
)
from app.services.ledger_service import ImmutableAuditLedger
from app.services.paypal_gateway import PayPalGateway


class SentinelArbiter:
    """Zero-Trust Policy Arbiter enforcing strict spending velocity, whitelist, and SLA verification."""

    def __init__(
        self,
        settings: Optional[Settings] = None,
        security_engine: Optional[SecurityEngine] = None,
        ledger: Optional[ImmutableAuditLedger] = None,
        paypal_gateway: Optional[PayPalGateway] = None,
    ):
        self.settings = settings or get_settings()
        self.security = security_engine or SecurityEngine(self.settings.SENTINEL_POLICY_HMAC_SECRET)
        self.ledger = ledger or ImmutableAuditLedger()
        self.paypal = paypal_gateway or PayPalGateway(self.settings)

        # In-memory tracking for velocity and escrow states
        self.approved_spends_log: List[Dict[str, any]] = []
        self.vendor_whitelist: Set[str] = {"verified_vendor_ai@enterprise.com", "cloud_compute_agent@vendor.org"}
        self.escrows: Dict[str, EscrowRecord] = {}

    def add_whitelisted_vendor(self, vendor_receiver: str):
        """Add an authorized vendor PayPal recipient."""
        self.vendor_whitelist.add(vendor_receiver)

    def evaluate_contract_proposal(self, proposal: ContractProposal) -> PolicyEvaluationResult:
        """Evaluate contract against zero-trust financial policies before escrow approval."""
        contract_id = proposal.contract_id

        # 1. Emergency Killswitch Check
        if self.settings.SENTINEL_EMERGENCY_KILLSWITCH:
            self.ledger.append_entry(
                action="POLICY_BLOCKED",
                contract_id=contract_id,
                data={"reason": "Emergency killswitch is active", "buyer": proposal.buyer_agent_id},
            )
            return PolicyEvaluationResult(
                approved=False,
                rejection_code="ERR_KILLSWITCH_ACTIVE",
                reason="System emergency killswitch is engaged. All transactions halted.",
                contract_id=contract_id,
            )

        # 2. Maximum Single Transaction Threshold Check
        if proposal.amount.value > self.settings.SENTINEL_MAX_SINGLE_TRANSACTION:
            self.ledger.append_entry(
                action="ROGUE_SPEND_BLOCKED",
                contract_id=contract_id,
                data={
                    "reason": "Exceeded single transaction limit",
                    "amount": str(proposal.amount.value),
                    "limit": str(self.settings.SENTINEL_MAX_SINGLE_TRANSACTION),
                },
            )
            return PolicyEvaluationResult(
                approved=False,
                rejection_code="ERR_MAX_SINGLE_LIMIT_EXCEEDED",
                reason=(
                    f"Transaction amount ${proposal.amount.value} exceeds maximum allowed "
                    f"single transaction cap of ${self.settings.SENTINEL_MAX_SINGLE_TRANSACTION}."
                ),
                contract_id=contract_id,
            )

        # 3. 24-Hour Rolling Spending Velocity Check
        now = datetime.utcnow()
        cutoff_24h = now - timedelta(hours=24)
        recent_total = sum(
            entry["amount"]
            for entry in self.approved_spends_log
            if entry["timestamp"] >= cutoff_24h and entry["buyer_agent_id"] == proposal.buyer_agent_id
        )
        if (recent_total + proposal.amount.value) > self.settings.SENTINEL_MAX_DAILY_VELOCITY:
            self.ledger.append_entry(
                action="VELOCITY_LIMIT_BLOCKED",
                contract_id=contract_id,
                data={
                    "reason": "Exceeded 24h rolling velocity cap",
                    "accumulated_24h": str(recent_total),
                    "attempted": str(proposal.amount.value),
                    "cap": str(self.settings.SENTINEL_MAX_DAILY_VELOCITY),
                },
            )
            return PolicyEvaluationResult(
                approved=False,
                rejection_code="ERR_DAILY_VELOCITY_EXCEEDED",
                reason=(
                    f"Transaction would push 24h spend (${recent_total + proposal.amount.value}) "
                    f"over daily velocity cap of ${self.settings.SENTINEL_MAX_DAILY_VELOCITY}."
                ),
                contract_id=contract_id,
            )

        # 4. Vendor Whitelist Validation
        if proposal.vendor_paypal_receiver not in self.vendor_whitelist:
            self.ledger.append_entry(
                action="ROGUE_VENDOR_BLOCKED",
                contract_id=contract_id,
                data={
                    "reason": "Vendor not in authorized whitelist",
                    "vendor_receiver": proposal.vendor_paypal_receiver,
                },
            )
            return PolicyEvaluationResult(
                approved=False,
                rejection_code="ERR_UNAUTHORIZED_VENDOR",
                reason=f"Target vendor '{proposal.vendor_paypal_receiver}' is not on the authorized recipient whitelist.",
                contract_id=contract_id,
            )

        # 5. Contract Cryptographic Signature Verification
        if proposal.signature:
            signable_dict = proposal.to_signable_dict()
            if not self.security.verify_signature(signable_dict, proposal.signature):
                self.ledger.append_entry(
                    action="SIGNATURE_TAMPER_DETECTED",
                    contract_id=contract_id,
                    data={"reason": "HMAC signature mismatch"},
                )
                return PolicyEvaluationResult(
                    approved=False,
                    rejection_code="ERR_SIGNATURE_MISMATCH",
                    reason="Contract cryptographic signature validation failed. Tampering detected.",
                    contract_id=contract_id,
                )

        # All policies satisfied - Authorize and log policy pass
        self.approved_spends_log.append(
            {
                "contract_id": contract_id,
                "buyer_agent_id": proposal.buyer_agent_id,
                "amount": proposal.amount.value,
                "timestamp": now,
            }
        )

        approval_signature = self.security.sign_contract(
            {"action": "APPROVE", "contract_id": contract_id, "amount": str(proposal.amount.value)}
        )
        self.ledger.append_entry(
            action="POLICY_APPROVED",
            contract_id=contract_id,
            data={"amount": str(proposal.amount.value), "signature": approval_signature},
        )

        # Initialize Escrow state
        self.escrows[contract_id] = EscrowRecord(
            escrow_id=f"escrow_{contract_id}",
            contract=proposal,
            status=EscrowStatus.POLICY_APPROVED,
        )

        return PolicyEvaluationResult(
            approved=True,
            reason="Contract satisfies all velocity, whitelist, and cryptographic security policies.",
            contract_id=contract_id,
            policy_signature=approval_signature,
        )

    async def initialize_paypal_escrow(self, contract_id: str) -> EscrowRecord:
        """Create PayPal Order v2 to hold escrow funds once policy is approved."""
        escrow = self.escrows.get(contract_id)
        if not escrow or escrow.status != EscrowStatus.POLICY_APPROVED:
            raise ValueError(f"Cannot hold escrow: Contract {contract_id} not in POLICY_APPROVED state.")

        order_res = await self.paypal.create_escrow_order(
            reference_id=contract_id,
            amount=str(escrow.contract.amount.value),
            currency=escrow.contract.amount.currency_code.value,
            description=f"Escrow hold for {escrow.contract.service_description}",
            idempotency_key=f"idemp_create_{contract_id}",
        )

        paypal_order_id = order_res.get("id")
        escrow.paypal_order_id = paypal_order_id
        escrow.status = EscrowStatus.FUNDS_HELD
        escrow.updated_at = datetime.utcnow()

        self.ledger.append_entry(
            action="ESCROW_FUNDS_HELD",
            contract_id=contract_id,
            data={"paypal_order_id": str(paypal_order_id)},
        )
        return escrow

    async def verify_and_settle_milestone(
        self,
        contract_id: str,
        milestone_id: str,
        delivered_proof: str,
    ) -> EscrowRecord:
        """Verify SLA milestone delivery hash and trigger autonomous PayPal settlement."""
        escrow = self.escrows.get(contract_id)
        if not escrow:
            raise ValueError(f"Escrow not found for contract {contract_id}")

        # Find target milestone
        milestone: Optional[SLAMilestone] = None
        for m in escrow.contract.milestones:
            if m.milestone_id == milestone_id:
                milestone = m
                break

        if not milestone:
            raise ValueError(f"Milestone {milestone_id} not defined in contract {contract_id}")

        # Verify delivered proof hash
        proof_hash = SecurityEngine.compute_sha256(delivered_proof)
        if proof_hash != milestone.expected_output_hash:
            self.ledger.append_entry(
                action="SLA_VERIFICATION_FAILED",
                contract_id=contract_id,
                data={
                    "milestone_id": milestone_id,
                    "expected": milestone.expected_output_hash,
                    "actual": proof_hash,
                },
            )
            raise ValueError(
                f"SLA Proof mismatch: Delivered content hash {proof_hash} != expected {milestone.expected_output_hash}"
            )

        # Mark milestone completed
        milestone.completed = True
        milestone.proof_data = {"raw_preview": delivered_proof[:100], "hash": proof_hash}
        escrow.status = EscrowStatus.SLA_VERIFIED

        self.ledger.append_entry(
            action="SLA_VERIFIED",
            contract_id=contract_id,
            data={"milestone_id": milestone_id, "proof_hash": proof_hash},
        )

        # Check if all milestones complete for settlement
        all_done = all(m.completed for m in escrow.contract.milestones)
        if all_done:
            # Capture the authorized order or disburse via Payout
            if escrow.paypal_order_id:
                capture_res = await self.paypal.capture_order(
                    order_id=escrow.paypal_order_id,
                    idempotency_key=f"idemp_cap_{contract_id}",
                )
                escrow.paypal_capture_id = capture_res.get("id")

            escrow.status = EscrowStatus.SETTLED
            escrow.updated_at = datetime.utcnow()

            self.ledger.append_entry(
                action="ESCROW_SETTLED",
                contract_id=contract_id,
                data={
                    "paypal_order_id": str(escrow.paypal_order_id),
                    "paypal_capture_id": str(escrow.paypal_capture_id),
                    "amount": str(escrow.contract.amount.value),
                },
            )

        return escrow
