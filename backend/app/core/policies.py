"""Dynamic Spend Policy and Escalation Tier Engine."""
from decimal import Decimal
from enum import Enum
from typing import Optional, Set
from pydantic import BaseModel, Field


class PolicyTier(str, Enum):
    TIER_1_LOW = "TIER_1_LOW"          # <= $50: Autonomous approval + instant PayPal Escrow Authorization
    TIER_2_MEDIUM = "TIER_2_MEDIUM"    # $50.01 - $200: Deep Nemotron Zero-Trust Audit + SHA-256 validation
    TIER_3_HIGH = "TIER_3_HIGH"        # > $200: PENDING_HUMAN_APPROVAL, biometric/admin credential sign-off


class PolicyConfig(BaseModel):
    tier_1_max: Decimal = Decimal("50.00")
    tier_2_max: Decimal = Decimal("200.00")
    hard_cap: Decimal = Decimal("1000.00")
    hourly_velocity_limit: Decimal = Decimal("2500.00")
    take_rate_percentage: Decimal = Decimal("3.50")
    whitelisted_agents: Set[str] = Field(default_factory=lambda: {
        "buyer_ai_procure_agent",
        "verified_vendor_ai@enterprise.com",
        "cloud_compute_agent@vendor.org",
        "hpc_cluster_node_9",
    })
    blacklisted_agents: Set[str] = Field(default_factory=lambda: {
        "compromised_hallucinating_agent_77",
        "unauthorized_rogue_hacker@darknet.io",
        "unauthorized_darkweb_syndicate@exploit.net",
    })


class TierEvaluation(BaseModel):
    tier: PolicyTier
    requires_human_approval: bool
    risk_score: int
    recommendation: str
    take_rate_fee: Decimal


class PolicyRuleEngine:
    """Evaluates dynamic transaction spending envelopes, tiers, and agent whitelists."""

    def __init__(self, config: Optional[PolicyConfig] = None):
        self.config = config or PolicyConfig()

    def update_config(self, **kwargs):
        """Update live vault configuration values."""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

    def evaluate_tier(self, amount: Decimal, agent_id: str, vendor_receiver: str) -> TierEvaluation:
        """Categorize transaction into Tier 1, 2, or 3 based on risk, volume, and blacklist rules."""
        # 1. Blacklist Check
        if agent_id in self.config.blacklisted_agents or vendor_receiver in self.config.blacklisted_agents:
            return TierEvaluation(
                tier=PolicyTier.TIER_3_HIGH,
                requires_human_approval=True,
                risk_score=99,
                recommendation="BLOCKED_BY_BLACKLIST: Immediate human security intervention required.",
                take_rate_fee=Decimal("0.00"),
            )

        fee = (amount * self.config.take_rate_percentage) / Decimal("100.00")

        # 2. Hard-Cap Check
        if amount > self.config.hard_cap:
            return TierEvaluation(
                tier=PolicyTier.TIER_3_HIGH,
                requires_human_approval=True,
                risk_score=95,
                recommendation=f"EXCEEDS_HARD_CAP (${self.config.hard_cap}): Escalating to human oversight.",
                take_rate_fee=fee,
            )

        # 3. Tier 1: Low (<= $50)
        if amount <= self.config.tier_1_max:
            return TierEvaluation(
                tier=PolicyTier.TIER_1_LOW,
                requires_human_approval=False,
                risk_score=5,
                recommendation="AUTONOMOUS_APPROVED: Instant PayPal escrow authorization permitted.",
                take_rate_fee=fee,
            )

        # 4. Tier 2: Medium ($50.01 - $200)
        elif amount <= self.config.tier_2_max:
            return TierEvaluation(
                tier=PolicyTier.TIER_2_MEDIUM,
                requires_human_approval=False,
                risk_score=25,
                recommendation="ZERO_TRUST_AUDIT_REQUIRED: Deep Nemotron verification with SHA-256 milestone lock.",
                take_rate_fee=fee,
            )

        # 5. Tier 3: High (> $200)
        else:
            return TierEvaluation(
                tier=PolicyTier.TIER_3_HIGH,
                requires_human_approval=True,
                risk_score=75,
                recommendation="PENDING_HUMAN_APPROVAL: Requires 1-click admin biometric credential sign-off.",
                take_rate_fee=fee,
            )


policy_engine = PolicyRuleEngine()
