"""Autonomous Vendor Agent: Fulfills services and delivers cryptographic SLA proofs."""
from typing import Dict
from app.core.security import SecurityEngine


class VendorAgent:
    """Agent representing service provider delivering verifiable computational work or data."""

    def __init__(self, agent_id: str, paypal_receiver: str):
        self.agent_id = agent_id
        self.paypal_receiver = paypal_receiver

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
