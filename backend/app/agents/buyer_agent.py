"""Autonomous Buyer Agent: Handles autonomous procurement negotiation, LLM reasoning, and signing."""
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional
from app.core.security import SecurityEngine
from app.models.schemas import ContractProposal, CurrencyCode, MoneyAmount, SLAMilestone
from app.services.llm_service import llm_service


class BuyerAgent:
    """Agent that formulates procurement envelopes using LLM reasoning and signs contracts."""

    def __init__(self, agent_id: str, security_engine: SecurityEngine):
        self.agent_id = agent_id
        self.security = security_engine

    async def reason_procurement_goal(self, goal: str, max_budget: Decimal) -> str:
        """Run Multi-LLM reasoning on user procurement intent."""
        system_prompt = (
            "You are BuyerAgent, an autonomous enterprise procurement AI. "
            "Analyze the procurement request, decompose milestones, evaluate cost efficiency, "
            "and state your proposed spending ceiling and delivery requirements in 2 concise sentences."
        )
        user_prompt = f"Target goal: '{goal}'. Hard budget ceiling: ${max_budget} USD."
        return await llm_service.generate_reasoning(system_prompt, user_prompt)

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
            deadline=datetime.now(timezone.utc) + timedelta(days=valid_days),
        )
        # Sign canonical payload
        signature = self.security.sign_contract(proposal.to_signable_dict())
        proposal.signature = signature
        return proposal
