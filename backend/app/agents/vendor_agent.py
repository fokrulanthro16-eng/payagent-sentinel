"""Autonomous Vendor Agent: Evaluates RFP terms using LLM reasoning and delivers cryptographic SLA proofs."""
from decimal import Decimal
from typing import Dict
from app.core.security import SecurityEngine
from app.services.llm_service import llm_service


class VendorAgent:
    """Agent representing service provider delivering verifiable computational work or data."""

    def __init__(self, agent_id: str, paypal_receiver: str):
        self.agent_id = agent_id
        self.paypal_receiver = paypal_receiver

    async def evaluate_rfp_proposal(self, goal: str, offered_amount: Decimal) -> str:
        """Run Multi-LLM reasoning on RFP acceptance."""
        system_prompt = (
            "You are VendorAgent, an autonomous HPC compute infrastructure provider. "
            "Analyze the client's procurement RFP, verify SLA deliverables, and respond with "
            "an acceptance agreement and SHA-256 deliverable guarantee in 2 crisp sentences."
        )
        user_prompt = f"Client requested: '{goal}' for ${offered_amount} USD."
        return await llm_service.generate_reasoning(system_prompt, user_prompt)

    def deliver_work(self, contract_id: str, milestone_id: str, raw_output: str) -> Dict[str, str]:
        """Deliver work and compute cryptographic SHA-256 proof hash."""
        output_hash = SecurityEngine.compute_sha256(raw_output)
        return {
            "contract_id": contract_id,
            "milestone_id": milestone_id,
            "vendor_agent_id": self.agent_id,
            "raw_output": raw_output,
            "proof_hash": output_hash,
        }
