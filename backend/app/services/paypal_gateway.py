"""PayPal REST API Client implementing Orders v2, Authorization, Capture & Payouts."""
import base64
import time
from typing import Any, Dict, Optional
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
    """Enterprise PayPal REST API client with OAuth2 token caching, Orders v2, and Payouts."""

    def __init__(self, settings: Optional[Settings] = None, client: Optional[httpx.AsyncClient] = None):
        self.settings = settings or get_settings()
        self._http_client = client
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0.0

    async def _get_client(self) -> httpx.AsyncClient:
        """Provide or create async HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def get_access_token(self, force_refresh: bool = False) -> str:
        """Fetch or return cached OAuth2 Bearer token from PayPal."""
        now = time.time()
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

    async def close(self):
        """Close HTTP client session."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
