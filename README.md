# PayAgent-Sentinel: Zero-Trust Multi-Agent Autonomous Escrow & Cryptographic Policy Engine

**Target Track:** Best Use of Agentic Commerce ($5,000) & Best Use of PayPal + AI ($5,000)  
**Hackathon:** PayPal AI Hackathon 2026

---

## Executive Summary

As autonomous AI agents acquire economic agency—negotiating deals, booking APIs, ordering compute clusters, and contracting services—they introduce catastrophic financial risk: **hallucinatory rogue spending**, runaway loops, prompt injection redirection, and unverified service delivery.

**PayAgent-Sentinel** introduces an enterprise **Zero-Trust Multi-Agent Autonomous Escrow and Cryptographic Policy Engine** backed directly by PayPal REST APIs (Orders v2 + Payouts). Autonomous buyer and vendor agents interact through a cryptographically bound policy arbiter that enforces mathematical spend constraints, dual-key SLA verification, and hash-chained immutable audit ledgers before triggering any real-world money movement.

---

## Key Pillars

1. **Deterministic Rogue Spend Interception (Sentinel Arbiter)**:
   - Dynamic spending velocity throttles (per-agent, per-transaction, and sliding 24-hour limits).
   - Domain and vendor whitelist enforcement.
   - Autonomous emergency kill-switch capability.
2. **Cryptographic Escrow Proofs**:
   - HMAC SHA-256 signed SLA contracts preventing tampering of terms between negotiation and settlement.
   - Dual-agent cryptographic milestone sign-offs.
3. **Enterprise PayPal REST API v2 Integration**:
   - Real-world integration with PayPal Sandbox/Live Orders v2 (Authorize & Capture).
   - Autonomous milestone-gated PayPal Payouts with idempotency keys.
4. **Immutable Audit Ledger**:
   - SHA-256 hash-chained block ledger recording every negotiation turn, policy evaluation, and financial trigger.
5. **Real-time AG Grid Telemetry Cockpit**:
   - Mission-control dashboard rendering agentic state transitions, policy interventions, and escrow releases.

---

## Architecture Overview

```
                      +-----------------------------+
                      |   Autonomous Buyer Agent    |
                      +--------------+--------------+
                                     |  1. Negotiate Contract
                                     v
                      +-----------------------------+
                      |   Autonomous Vendor Agent   |
                      +--------------+--------------+
                                     |  2. Submit Signed SLA Proposal
                                     v
        +--------------------------------------------------------+
        |                Sentinel Policy Arbiter                 |
        |  * Velocity Limits Check   * Hash Chain Verification   |
        |  * Vendor Whitelist        * HMAC Signature Match      |
        +----------------------------+---------------------------+
                                     |  3. Policy Verdict
                   +-----------------+-----------------+
                   | Approved                          | Rejected
                   v                                   v
    +------------------------------+     +-------------------------------+
    |    PayPal Orders v2 Escrow   |     | Hard Rejection & Rogue Alert  |
    |  * Create Order & Authorize  |     | Logged to Hash-Chained Ledger |
    +--------------+---------------+     +-------------------------------+
                   | 4. SLA Proof Verified
                   v
    +------------------------------+
    |   PayPal Capture / Payout    |
    |  * Disburse to Vendor Wallet |
    +------------------------------+
```

---

## Repository Structure

```
payagent-sentinel/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py             # Environment & credentials loader
│   │   │   └── security.py           # HMAC SHA-256 policy signature engine
│   │   ├── models/
│   │   │   └── schemas.py            # Pydantic v2 strict schemas (Policies, Escrow, Invoices)
│   │   ├── services/
│   │   │   ├── paypal_gateway.py     # PayPal REST API (OAuth2, Orders v2, Capture, Payouts)
│   │   │   └── ledger_service.py     # Immutable hash-chained audit ledger
│   │   ├── agents/
│   │   │   ├── buyer_agent.py        # Autonomous procurement negotiator
│   │   │   ├── vendor_agent.py       # Autonomous service provider & SLA proof submitter
│   │   │   └── sentinel_arbiter.py   # Zero-trust policy verifier & rogue spend blocker
│   │   └── main.py                   # FastAPI application with REST endpoints & WebSockets
│   ├── tests/
│   │   ├── test_paypal_client.py     # Mocked & sandbox tests
│   │   ├── test_policy_engine.py     # Rogue spend interception verification
│   │   └── test_escrow_settlement.py # End-to-end multi-agent settlement flow
│   ├── requirements.txt
│   └── .env.example
├── frontend/                         # Next.js / Vite AG Grid Telemetry Cockpit
├── docs/                             # Architecture diagrams & API documentation
├── render.yaml                       # Cloud deployment blueprint
└── LICENSE                           # Apache-2.0
```

---

## Quickstart

### Prerequisites
- Python 3.11+
- PayPal Sandbox Developer Account (`client_id` & `client_secret`)

### Setup & Run Tests
```bash
cd backend
pip install -r requirements.txt
pytest -v
```

### Launch API Service
```bash
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at `http://localhost:8000/docs`.

---

## License
Apache-2.0. Built for the PayPal AI Hackathon 2026.
