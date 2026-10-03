"""Test suite for PayPal Gateway REST API operations with mocks and sandbox simulation."""
import pytest
import httpx
from app.core.config import Settings
from app.services.paypal_gateway import PayPalGateway, PayPalAPIError


@pytest.fixture
def test_settings():
    return Settings(
        PAYPAL_ENV="sandbox",
        PAYPAL_CLIENT_ID="test_client_id",
        PAYPAL_CLIENT_SECRET="test_client_secret",
    )


@pytest.mark.asyncio
async def test_paypal_token_caching(test_settings):
    """Test OAuth2 client credential token fetching and caching behavior."""
    call_count = 0

    def mock_handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        if request.url.path == "/v1/oauth2/token":
            return httpx.Response(
                200,
                json={"access_token": "mocked_bearer_token_xyz", "expires_in": 3600, "token_type": "Bearer"},
            )
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        gateway = PayPalGateway(settings=test_settings, client=client)

        token1 = await gateway.get_access_token()
        token2 = await gateway.get_access_token()

        assert token1 == "mocked_bearer_token_xyz"
        assert token2 == "mocked_bearer_token_xyz"
        assert call_count == 1  # Verify token was cached


@pytest.mark.asyncio
async def test_paypal_create_and_capture_order(test_settings):
    """Test full order creation and capture lifecycle against PayPal API."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/v1/oauth2/token":
            return httpx.Response(
                200,
                json={"access_token": "mock_token", "expires_in": 3600},
            )
        elif request.url.path == "/v2/checkout/orders":
            return httpx.Response(
                201,
                json={"id": "ORDER_12345", "status": "CREATED"},
            )
        elif request.url.path == "/v2/checkout/orders/ORDER_12345/capture":
            return httpx.Response(
                201,
                json={"id": "CAPTURE_67890", "status": "COMPLETED"},
            )
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        gateway = PayPalGateway(settings=test_settings, client=client)

        order_res = await gateway.create_escrow_order(
            reference_id="contract_test_001",
            amount="250.00",
            currency="USD",
        )
        assert order_res["id"] == "ORDER_12345"
        assert order_res["status"] == "CREATED"

        capture_res = await gateway.capture_order(order_id="ORDER_12345")
        assert capture_res["id"] == "CAPTURE_67890"
        assert capture_res["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_paypal_error_handling(test_settings):
    """Verify PayPalAPIError is raised on 401 unauthorized or invalid credentials."""

    def mock_handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            401,
            json={"error": "invalid_client", "error_description": "Client Authentication failed"},
        )

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        gateway = PayPalGateway(settings=test_settings, client=client)

        with pytest.raises(PayPalAPIError) as exc_info:
            await gateway.get_access_token()
        assert exc_info.value.status_code == 401
