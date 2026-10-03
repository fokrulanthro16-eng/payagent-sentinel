"""Cryptographic Policy Signature and Verification Engine."""
import hashlib
import hmac
import json
from typing import Any, Dict


class SecurityEngine:
    """Cryptographic utility for HMAC-SHA256 signatures and payload hashing."""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key.encode("utf-8")

    def canonicalize(self, payload: Dict[str, Any]) -> bytes:
        """Convert payload into deterministic canonical JSON byte representation."""
        # Sort keys and remove whitespace separators to ensure identical representation
        return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def sign_contract(self, payload: Dict[str, Any]) -> str:
        """Generate HMAC-SHA256 hex signature for given contract dictionary."""
        canonical_bytes = self.canonicalize(payload)
        return hmac.new(self.secret_key, canonical_bytes, hashlib.sha256).hexdigest()

    def verify_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """Verify HMAC-SHA256 signature against payload using constant-time comparison."""
        expected_signature = self.sign_contract(payload)
        return hmac.compare_digest(expected_signature, signature)

    @staticmethod
    def compute_sha256(data: str | bytes) -> str:
        """Compute SHA256 digest of input."""
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.sha256(data).hexdigest()
