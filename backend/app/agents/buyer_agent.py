"""Autonomous Buyer Agent: Handles autonomous procurement negotiation and contract signing."""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from app.core.security import SecurityEngine
from app.models.schemas import ContractProposal, CurrencyCode, MoneyAmount, SLAMilestone


class BuyerAgent:
    """Agent that creates structured procurement proposals with cryptographic signatures."""

    def __init__(self, agent_id: str, security_engine: SecurityEngine):
        self.agent_id = agent_id
        self.security = security_engine

    def formulate_contract_proposal(
        self,
        contract_id: str,
        vendor_agent_id: str,
        vendor_paypal_receiver: str,
        service_description: str,
        amount: Decimal,
        milestones: List[SLAMilestone],
        currency: CurrencyCode = CurrencyCode.USD,
        valid_days: int = 7,
    ) -> ContractProposal:
        """Create and cryptographically sign a contract proposal."""
        proposal = ContractProposal(
            contract_id=contract_id,
            buyer_agent_id=self.agent_id,
            vendor_agent_id=vendor_agent_id,
            vendor_paypal_receiver=vendor_paypal_receiver,
            service_description=service_description,
            amount=MoneyAmount(currency_code=currency, value=amount),
            milestones=milestones,
            deadline=datetime.utcnow() + timedelta(days=valid_days),
        )
        # Sign canonical payload
        signature = self.security.sign_contract(proposal.to_signable_dict())
        proposal.signature = signature
        return proposal
