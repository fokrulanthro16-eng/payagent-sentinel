"""Cryptographically hash-chained immutable audit ledger."""
from datetime import datetime
import json
from typing import Dict, List, Optional
from app.core.security import SecurityEngine
from app.models.schemas import LedgerBlock


class ImmutableAuditLedger:
    """Tamper-evident, hash-chained ledger storing all multi-agent actions and financial events."""

    def __init__(self, genesis_label: str = "GENESIS_SENTINEL_ROOT"):
        self.chain: List[LedgerBlock] = []
        self._initialize_chain(genesis_label)

    def _initialize_chain(self, genesis_label: str):
        """Build genesis block."""
        genesis_data = {"event": "LEDGER_INITIALIZED", "label": genesis_label}
        genesis_hash = SecurityEngine.compute_sha256(
            f"0:0000000000000000000000000000000000000000000000000000000000000000:{json.dumps(genesis_data, sort_keys=True)}"
        )
        block = LedgerBlock(
            index=0,
            timestamp=datetime.utcnow(),
            action="GENESIS",
            contract_id="system",
            data=genesis_data,
            previous_hash="0" * 64,
            block_hash=genesis_hash,
        )
        self.chain.append(block)

    def append_entry(self, action: str, contract_id: str, data: Dict[str, str]) -> LedgerBlock:
        """Append a new verified entry to the hash chain."""
        previous_block = self.chain[-1]
        next_index = previous_block.index + 1
        now = datetime.utcnow()

        raw_block_data = (
            f"{next_index}:{previous_block.block_hash}:{action}:{contract_id}:"
            f"{json.dumps(data, sort_keys=True)}:{now.isoformat()}"
        )
        current_hash = SecurityEngine.compute_sha256(raw_block_data)

        new_block = LedgerBlock(
            index=next_index,
            timestamp=now,
            action=action,
            contract_id=contract_id,
            data=data,
            previous_hash=previous_block.block_hash,
            block_hash=current_hash,
        )
        self.chain.append(new_block)
        return new_block

    def verify_integrity(self) -> bool:
        """Verify the cryptographic hash link across the entire chain."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]

            if current.previous_hash != prev.block_hash:
                return False

            raw_block_data = (
                f"{current.index}:{current.previous_hash}:{current.action}:{current.contract_id}:"
                f"{json.dumps(current.data, sort_keys=True)}:{current.timestamp.isoformat()}"
            )
            recomputed = SecurityEngine.compute_sha256(raw_block_data)
            if current.block_hash != recomputed:
                return False

        return True

    def get_entries_for_contract(self, contract_id: str) -> List[LedgerBlock]:
        """Return all ledger blocks associated with a specific contract."""
        return [b for b in self.chain if b.contract_id == contract_id]
