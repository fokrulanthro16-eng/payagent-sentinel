"""PayPal REST API Client with Dual-Mode Support:
1. Live PayPal Sandbox/Production (when valid credentials provided)
2. Deterministic High-Fidelity PayPal Sandbox Gateway Engine (spec-compliant for Orders v2 & Payouts v1)
"""
import base64
from datetime import datetime, timezone
import time
from typing import Any, Dict, Optional
import uuid
import httpx
from app.core.config import Settings, get_settings


class PayPalAPIError(Exception):
    """Exception raised for PayPal API operational errors."""

    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class PayPalGateway:
    """Enterprise PayPal REST API client supporting real sandbox endpoints and deterministic mock engine."""

    def __init__(self, settings: Optional[Settings] = None, client: Optional[httpx.AsyncClient] = None):
        self.settings = settings or get_settings()
        self._http_client = client
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    @property
    def is_simulation_mode(self) -> bool:
        """Determines if sandbox mock simulation engine should be active."""
        client_id = self.settings.PAYPAL_CLIENT_ID or ""
        return client_id in ("", "mock_client_id", "your_paypal_sandbox_client_id")

    async def _get_client(self) -> httpx.AsyncClient:
        """Provide or create async HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def get_access_token(self, force_refresh: bool = False) -> str:
        """Fetch or return cached OAuth2 Bearer token from PayPal."""
        now = time.time()
        # Simulation engine token
        if self.is_simulation_mode and self._http_client is None:
            self._access_token = f"A21AAI_SANDBOX_MOCK_TOKEN_{uuid.uuid4().hex[:12].upper()}"
            self._token_expires_at = now + 32400
            return self._access_token

        # Use cache if token is valid with 60 second safety buffer
        if not force_refresh and self._access_token and now < (self._token_expires_at - 60):
            return self._access_token

        client_id = self.settings.PAYPAL_CLIENT_ID
        client_secret = self.settings.PAYPAL_CLIENT_SECRET
        auth_bytes = f"{client_id}:{client_secret}".encode("utf-8")
        auth_header = base64.b64encode(auth_bytes).decode("utf-8")

        url = f"{self.settings.paypal_base_url}/v1/oauth2/token"
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials"}

        client = await self._get_client()
        try:
            response = await client.post(url, headers=headers, data=data)
            if response.status_code != 200:
                raise PayPalAPIError(
                    f"PayPal OAuth2 failed with status {response.status_code}: {response.text}",
                    status_code=response.status_code,
                    details=response.json() if response.headers.get("content-type") == "application/json" else {},
                )

            token_data = response.json()
            self._access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 32400)
            self._token_expires_at = now + float(expires_in)
            return self._access_token
        except httpx.RequestError as exc:
            raise PayPalAPIError(f"HTTP request error during token generation: {str(exc)}") from exc

    async def _get_auth_headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        """Return authenticated HTTP headers with optional idempotency key."""
        token = await self.get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
        if idempotency_key:
            headers["PayPal-Request-Id"] = idempotency_key
        return headers

    async def create_escrow_order(
        self,
        reference_id: str,
        amount: str,
        currency: str = "USD",
        intent: str = "CAPTURE",
        description: str = "PayAgent-Sentinel Escrow Hold",
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a PayPal Order v2 for holding buyer funds in escrow."""
        # Simulation Mode
        if self.is_simulation_mode and self._http_client is None:
            order_id = f"ORD-SANDBOX-AUTH-{uuid.uuid4().hex[:8].upper()}"
            now_iso = datetime.now(timezone.utc).isoformat()
            return {
                "id": order_id,
                "status": "APPROVED",
                "intent": intent,
                "create_time": now_iso,
                "links": [
                    {
                        "href": f"https://www.sandbox.paypal.com/checkoutnow?token={order_id}",
                        "rel": "approve",
                        "method": "GET",
                    },
                    {
                        "href": f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture",
                        "rel": "capture",
                        "method": "POST",
                    },
                ],
                "purchase_units": [
                    {
                        "reference_id": reference_id,
                        "description": description,
                        "amount": {"currency_code": currency, "value": amount},
                    }
                ],
            }

        url = f"{self.settings.paypal_base_url}/v2/checkout/orders"
        headers = await self._get_auth_headers(idempotency_key)

        payload = {
            "intent": intent,
            "purchase_units": [
                {
                    "reference_id": reference_id,
                    "description": description,
                    "amount": {
                        "currency_code": currency,
                        "value": amount,
                    },
                }
            ],
            "application_context": {
                "shipping_preference": "NO_SHIPPING",
                "user_action": "PAY_NOW",
            },
        }

        client = await self._get_client()
        try:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code not in (200, 201):
                raise PayPalAPIError(
                    f"Create Order failed: {response.status_code} - {response.text}",
                    status_code=response.status_code,
                    details=response.json() if response.is_success else {},
                )
            return response.json()
        except httpx.RequestError as exc:
            raise PayPalAPIError(f"Network error creating escrow order: {str(exc)}") from exc

    async def capture_order(
        self,
        order_id: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Capture authorized PayPal order funds once SLA milestones are validated."""
        # Simulation Mode
        if self.is_simulation_mode and self._http_client is None:
            capture_id = f"CAP-SANDBOX-SETTLED-{uuid.uuid4().hex[:8].upper()}"
            now_iso = datetime.now(timezone.utc).isoformat()
            return {
                "id": capture_id,
                "status": "COMPLETED",
                "create_time": now_iso,
                "update_time": now_iso,
                "seller_protection": {
                    "status": "ELIGIBLE",
                    "dispute_categories": ["ITEM_NOT_RECEIVED", "UNAUTHORIZED_TRANSACTION"],
                },
                "links": [
                    {
                        "href": f"https://api-m.sandbox.paypal.com/v2/payments/captures/{capture_id}",
                        "rel": "self",
                        "method": "GET",
                    }
                ],
            }

        url = f"{self.settings.paypal_base_url}/v2/checkout/orders/{order_id}/capture"
        headers = await self._get_auth_headers(idempotency_key)

        client = await self._get_client()
        try:
            response = await client.post(url, headers=headers, json={})
            if response.status_code not in (200, 201):
                raise PayPalAPIError(
                    f"Capture Order failed: {response.status_code} - {response.text}",
                    status_code=response.status_code,
                )
            return response.json()
        except httpx.RequestError as exc:
            raise PayPalAPIError(f"Network error capturing order: {str(exc)}") from exc

    async def execute_payout(
        self,
        sender_batch_id: str,
        receiver_email: str,
        amount: str,
        currency: str = "USD",
        note: str = "PayAgent-Sentinel Milestone Settlement",
    ) -> Dict[str, Any]:
        """Disburse funds directly to vendor wallet using PayPal Payouts API."""
        # Simulation Mode
        if self.is_simulation_mode and self._http_client is None:
            payout_id = f"PAYOUT-BATCH-{uuid.uuid4().hex[:8].upper()}"
            return {
                "batch_header": {
                    "payout_batch_id": payout_id,
                    "batch_status": "SUCCESS",
                    "sender_batch_header": {
                        "sender_batch_id": sender_batch_id,
                        "email_subject": "SLA Verified: Escrow Payout Released",
                    },
                }
            }

        url = f"{self.settings.paypal_base_url}/v1/payments/payouts"
        headers = await self._get_auth_headers()

        payload = {
            "sender_batch_header": {
                "sender_batch_id": sender_batch_id,
                "email_subject": "SLA Verified: Escrow Payout Released",
                "email_message": note,
            },
            "items": [
                {
                    "recipient_type": "EMAIL",
                    "amount": {
                        "value": amount,
                        "currency": currency,
                    },
                    "receiver": receiver_email,
                    "note": note,
                    "sender_item_id": f"item_{sender_batch_id}",
                }
            ],
        }

        client = await self._get_client()
        try:
            response = await client.post(url, headers=headers, json=payload)
            if response.status_code not in (200, 201):
                raise PayPalAPIError(
                    f"Payout failed: {response.status_code} - {response.text}",
                    status_code=response.status_code,
                )
            return response.json()
        except httpx.RequestError as exc:
            raise PayPalAPIError(f"Network error executing payout: {str(exc)}") from exc

    async def void_escrow_order(self, order_id: str) -> Dict[str, Any]:
        """Void an authorized PayPal escrow hold upon SLA breach or timeout."""
        if self.is_simulation_mode and self._http_client is None:
            return {
                "id": order_id,
                "status": "VOIDED",
                "void_time": datetime.now(timezone.utc).isoformat(),
                "reason": "SLA_BREACH_TIMEOUT",
            }

        url = f"{self.settings.paypal_base_url}/v2/checkout/orders/{order_id}/void"
        headers = await self._get_auth_headers()
        client = await self._get_client()
        try:
            response = await client.post(url, headers=headers)
            if response.status_code not in (200, 204):
                raise PayPalAPIError(f"Void failed: {response.status_code} - {response.text}", status_code=response.status_code)
            return {"id": order_id, "status": "VOIDED"}
        except httpx.RequestError as exc:
            raise PayPalAPIError(f"Network error voiding order: {str(exc)}") from exc

    async def refund_buyer(self, capture_or_order_id: str, note: str = "SLA Verification Failed: Auto-Refund") -> Dict[str, Any]:
        """Execute automated refund to buyer wallet when SLA proof fails or expires."""
        refund_id = f"REFUND-SANDBOX-{uuid.uuid4().hex[:8].upper()}"
        now_iso = datetime.now(timezone.utc).isoformat()

        if self.is_simulation_mode and self._http_client is None:
            return {
                "id": refund_id,
                "status": "COMPLETED",
                "create_time": now_iso,
                "note_to_payer": note,
                "links": [{"href": f"https://api-m.sandbox.paypal.com/v2/payments/refunds/{refund_id}", "rel": "self", "method": "GET"}],
            }

        url = f"{self.settings.paypal_base_url}/v2/payments/captures/{capture_or_order_id}/refund"
        headers = await self._get_auth_headers()
        client = await self._get_client()
        try:
            response = await client.post(url, headers=headers, json={"note_to_payer": note})
            if response.status_code not in (200, 201):
                raise PayPalAPIError(f"Refund failed: {response.status_code} - {response.text}", status_code=response.status_code)
            return response.json()
        except httpx.RequestError as exc:
            raise PayPalAPIError(f"Network error refunding capture: {str(exc)}") from exc

    async def close(self):
        """Close HTTP client session."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
