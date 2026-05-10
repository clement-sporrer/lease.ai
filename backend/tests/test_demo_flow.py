"""Demo-extras routers smoke test.

Only exercises the in-memory demo backend (refi, offers, contracts, assets,
billing, dashboards, ai, demo). The real DB-backed routers (deals, companies,
quotes, documents, pricing, risk, admin, me, auth) live on `main` and require
a Postgres + Supabase environment — they are covered by their own tests.
"""
import pytest
from fastapi.testclient import TestClient

from app import state as app_state
from app.main import app


@pytest.fixture()
def client():
    app_state.reset()
    return TestClient(app)


PARTNER = {"X-Demo-Email": "partner@leaseai.demo"}
ADMIN = {"X-Demo-Email": "admin@leaseai.demo"}
FINANCIER = {"X-Demo-Email": "financier@leaseai.demo"}
CLIENT = {"X-Demo-Email": "client@leaseai.demo"}
CFO = {"X-Demo-Email": "cfo@leaseai.demo"}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "LeaseAI API"


def test_demo_users_listed(client):
    r = client.get("/demo/users", headers=ADMIN)
    assert r.status_code == 200
    body = r.json()
    emails = [u["email"] for u in body["data"]]
    assert "partner@leaseai.demo" in emails
    assert "admin@leaseai.demo" in emails
    assert "cfo@leaseai.demo" in emails


def test_demo_reset(client):
    r = client.post("/demo/reset", headers=ADMIN)
    assert r.status_code == 200
    assert r.json()["data"]["deals"] == 3


def test_demo_snapshot(client):
    r = client.get("/demo/snapshot", headers=ADMIN)
    assert r.status_code == 200
    counts = r.json()["data"]["counts"]
    assert counts["deals"] == 3
    assert counts["companies"] == 3


def test_static_pdf_served(client):
    r = client.get("/static/refi_demo.pdf")
    assert r.status_code == 200
    assert r.content.startswith(b"%PDF-1.4")


def test_cfo_portfolio(client):
    r = client.get("/dashboards/cfo/portfolio", headers=CFO)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["active_leases"] >= 12
    assert data["total_commitment_eur"] >= 2_450_000


def test_cfo_cash(client):
    r = client.get("/dashboards/cfo/cash", headers=CFO)
    assert r.status_code == 200
    data = r.json()["data"]
    assert "expected_next_30d_cents" in data


def test_cfo_risk(client):
    r = client.get("/dashboards/cfo/risk", headers=CFO)
    assert r.status_code == 200


def test_partner_dashboard(client):
    r = client.get("/dashboards/partner", headers=PARTNER)
    assert r.status_code == 200
    assert "kpis" in r.json()["data"]


def test_admin_dashboard(client):
    r = client.get("/dashboards/admin", headers=ADMIN)
    assert r.status_code == 200


def test_client_dashboard(client):
    r = client.get("/dashboards/client", headers=CLIENT)
    assert r.status_code == 200


def test_refi_to_active_demo_path(client):
    """Pre-seed a deal in pre_approved status, then run refi → active."""
    deal_id = "deal_globex_001"
    with app_state.state_lock():
        deal = app_state.db()["deals"][deal_id]
        deal["status"] = "pre_approved"
        deal["risk_score"] = 82
        deal["risk_band"] = "A"
        deal["monthly_payment_cents"] = 261000

    r = client.post(f"/deals/{deal_id}/refi-package", headers=ADMIN)
    assert r.status_code == 201, r.text
    pkg = r.json()["data"]

    r = client.post(f"/refi-packages/{pkg['id']}/send", headers=ADMIN)
    assert r.status_code == 200

    r = client.get(f"/refi-packages/{pkg['id']}", headers=FINANCIER)
    assert r.status_code == 200

    r = client.post(
        f"/refi-packages/{pkg['id']}/decision",
        json={"decision": "approved", "comment": "OK"},
        headers=FINANCIER,
    )
    assert r.status_code == 200, r.text

    r = client.post(f"/deals/{deal_id}/offers", headers=ADMIN)
    assert r.status_code == 201
    offer = r.json()["data"]
    assert offer["amount_cents"] > 0

    r = client.post(f"/deals/{deal_id}/contracts", headers=ADMIN)
    assert r.status_code == 201
    contract = r.json()["data"]

    r = client.post(f"/contracts/{contract['id']}/mock-sign", headers=ADMIN)
    assert r.status_code == 200, r.text
    assert r.json()["data"]["status"] == "signed"

    r = client.get(f"/contracts/{contract['id']}/activation-checklist", headers=ADMIN)
    assert r.status_code == 200

    r = client.post(f"/contracts/{contract['id']}/activate", headers=ADMIN)
    assert r.status_code == 200, r.text
    assert r.json()["data"]["status"] == "active"

    r = client.get(f"/contracts/{contract['id']}/schedule", headers=CLIENT)
    assert r.status_code == 200
    assert len(r.json()["data"]) > 0

    r = client.get(f"/contracts/{contract['id']}/assets", headers=CLIENT)
    assert r.status_code == 200
    assert len(r.json()["data"]) > 0

    r = client.post(f"/contracts/{contract['id']}/invoices", headers=ADMIN)
    assert r.status_code == 201
    invoice = r.json()["data"]

    r = client.post(f"/invoices/{invoice['id']}/mark-paid", headers=ADMIN)
    assert r.status_code == 200
    body = r.json()["data"]
    assert body["invoice"]["status"] == "paid"
    assert body["payment"]["status"] == "received"


def test_pricing_and_risk_helpers(client):
    from app.services.pricing_calc import compute_indicative
    from app.services.risk_calc import assess

    pricing = compute_indicative(
        amount_cents=8550000, duration_months=36, category="Laptops & Accessories", band="A"
    )
    assert pricing["monthly_payment_cents"] > 0
    assert pricing["duration_months"] == 36

    company = {"active_status": True, "creation_date": "2016-05-12"}
    deal = {"amount_cents": 8550000, "category": "Laptops & Accessories"}
    risk = assess(company=company, deal=deal)
    assert risk["band"] in ("A", "B", "C", "D", "E")
    assert risk["score"] >= 0


def test_404_envelope(client):
    r = client.get("/contracts/does_not_exist", headers=ADMIN)
    assert r.status_code == 404
    body = r.json()
    assert body["errors"][0]["code"] == "ENTITY_NOT_FOUND"


def test_ai_assistant_query(client):
    r = client.post(
        "/ai/assistant/query",
        json={"question": "où en est le dossier ?", "deal_id": "deal_globex_001"},
        headers=ADMIN,
    )
    assert r.status_code == 200
    assert "answer" in r.json()["data"]


def test_ai_deal_summary(client):
    r = client.post("/ai/deals/deal_globex_001/summary", headers=ADMIN)
    assert r.status_code == 200
    body = r.json()["data"]
    assert "summary" in body
    assert "next_action" in body


def test_demo_auth_anonymous_falls_back(client):
    """No header in demo mode = treated as admin."""
    r = client.get("/demo/snapshot")
    assert r.status_code == 200
