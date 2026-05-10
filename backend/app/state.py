"""In-memory state for demo. Single source of truth across all routers.

Reset via POST /demo/reset. Survives until process restart.
Thread-safe via single lock; FastAPI runs handlers in threadpool by default
for sync defs, asyncio loop for async — we use sync handlers, no contention.
"""
from __future__ import annotations

import copy
import threading
import time
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any

_lock = threading.RLock()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


# ---------------------------------------------------------------------------
# Seed
# ---------------------------------------------------------------------------


def _build_seed() -> dict[str, Any]:
    now = _now_iso()

    organizations = {
        "org_partner_001": {
            "id": "org_partner_001",
            "type": "partner",
            "legal_name": "Tech Solutions Partner SAS",
            "trade_name": "Tech Solutions Partner",
            "siren": "111222333",
            "siret": "11122233300011",
            "address": "5 rue de Rivoli, 75001 Paris",
            "status": "active",
            "quality_band": "A",
        },
        "org_client_001": {
            "id": "org_client_001",
            "type": "client",
            "legal_name": "Globex Inc.",
            "trade_name": "Globex",
            "siren": "123456789",
            "siret": "12345678900012",
            "address": "12 Avenue de l'Opéra, 75002 Paris",
            "status": "active",
        },
        "org_financier_001": {
            "id": "org_financier_001",
            "type": "financier",
            "legal_name": "Blue Capital Finance",
            "trade_name": "Blue Capital",
            "siren": "555666777",
            "siret": "55566677700019",
            "address": "1 Place Vendôme, 75001 Paris",
            "status": "active",
        },
        "org_internal_001": {
            "id": "org_internal_001",
            "type": "internal",
            "legal_name": "LeaseAI",
            "trade_name": "LeaseAI",
            "siren": "999888777",
            "siret": "99988877700015",
            "address": "10 Boulevard Haussmann, 75009 Paris",
            "status": "active",
        },
    }

    users = {
        "user_partner_001": {
            "id": "user_partner_001",
            "email": "partner@leaseai.demo",
            "full_name": "Emma Martin",
            "phone": "+33612345678",
            "active_role": "partner",
            "roles": ["partner"],
            "organization_id": "org_partner_001",
            "status": "active",
        },
        "user_admin_001": {
            "id": "user_admin_001",
            "email": "admin@leaseai.demo",
            "full_name": "Clara Ops",
            "phone": "+33611111111",
            "active_role": "admin",
            "roles": ["admin", "ops"],
            "organization_id": "org_internal_001",
            "status": "active",
        },
        "user_ops_001": {
            "id": "user_ops_001",
            "email": "ops@leaseai.demo",
            "full_name": "Paul Ops",
            "phone": "+33611111112",
            "active_role": "ops",
            "roles": ["ops"],
            "organization_id": "org_internal_001",
            "status": "active",
        },
        "user_risk_001": {
            "id": "user_risk_001",
            "email": "risk@leaseai.demo",
            "full_name": "Hugo Risk",
            "phone": "+33611111113",
            "active_role": "ops",
            "roles": ["ops"],
            "organization_id": "org_internal_001",
            "status": "active",
        },
        "user_financier_001": {
            "id": "user_financier_001",
            "email": "financier@leaseai.demo",
            "full_name": "Martin Finance",
            "phone": "+33622222222",
            "active_role": "financier",
            "roles": ["financier"],
            "organization_id": "org_financier_001",
            "status": "active",
        },
        "user_client_001": {
            "id": "user_client_001",
            "email": "client@leaseai.demo",
            "full_name": "Sophie Client",
            "phone": "+33633333333",
            "active_role": "client",
            "roles": ["client"],
            "organization_id": "org_client_001",
            "status": "active",
        },
        "user_cfo_001": {
            "id": "user_cfo_001",
            "email": "cfo@leaseai.demo",
            "full_name": "Lea CFO",
            "phone": "+33644444444",
            "active_role": "cfo",
            "roles": ["cfo"],
            "organization_id": "org_internal_001",
            "status": "active",
        },
    }

    companies = {
        "cmp_globex_001": {
            "id": "cmp_globex_001",
            "siren": "123456789",
            "siret": "12345678900012",
            "legal_name": "Globex Inc.",
            "trade_name": "Globex",
            "address": "12 Avenue de l'Opéra, 75002 Paris",
            "activity_code": "6202A",
            "activity_label": "Conseil en systèmes informatiques",
            "creation_date": "2016-05-12",
            "legal_status": "SAS",
            "active_status": True,
            "director_name": "Mathieu Globex",
            "enrichment_source": "pappers_mock",
            "enrichment_payload_json": {"capital_eur": 50000, "employees": 42},
            "created_at": now,
        },
        "cmp_acme_001": {
            "id": "cmp_acme_001",
            "siren": "987654321",
            "siret": "98765432100018",
            "legal_name": "Acme Corporation",
            "trade_name": "Acme",
            "address": "21 rue de la Paix, 75002 Paris",
            "activity_code": "4651Z",
            "activity_label": "Commerce de gros d'ordinateurs",
            "creation_date": "2018-09-03",
            "legal_status": "SARL",
            "active_status": True,
            "director_name": "Lucia Acme",
            "enrichment_source": "pappers_mock",
            "enrichment_payload_json": {"capital_eur": 30000, "employees": 18},
            "created_at": now,
        },
        "cmp_umbrella_001": {
            "id": "cmp_umbrella_001",
            "siren": "456789123",
            "siret": "45678912300023",
            "legal_name": "Umbrella Corp.",
            "trade_name": "Umbrella",
            "address": "8 Place de la République, 75003 Paris",
            "activity_code": "7022Z",
            "activity_label": "Conseil pour les affaires",
            "creation_date": "2020-01-15",
            "legal_status": "SAS",
            "active_status": True,
            "director_name": "Albert Wesker",
            "enrichment_source": "pappers_mock",
            "enrichment_payload_json": {"capital_eur": 10000, "employees": 9},
            "created_at": now,
        },
    }

    deals = {
        "deal_globex_001": {
            "id": "deal_globex_001",
            "public_id": "D-2026-0001",
            "company_id": "cmp_globex_001",
            "partner_org_id": "org_partner_001",
            "client_org_id": "org_client_001",
            "submitted_by_user_id": "user_partner_001",
            "status": "draft",
            "amount_cents": 8550000,
            "currency": "EUR",
            "duration_months": 36,
            "payment_frequency": "monthly",
            "category": "Laptops & Accessories",
            "risk_score": None,
            "risk_band": None,
            "monthly_payment_cents": None,
            "missing_documents": [],
            "created_at": now,
            "updated_at": now,
        },
        "deal_acme_001": {
            "id": "deal_acme_001",
            "public_id": "D-2026-0002",
            "company_id": "cmp_acme_001",
            "partner_org_id": "org_partner_001",
            "client_org_id": None,
            "submitted_by_user_id": "user_partner_001",
            "status": "draft",
            "amount_cents": 12000000,
            "currency": "EUR",
            "duration_months": 48,
            "payment_frequency": "monthly",
            "category": "Network",
            "risk_score": None,
            "risk_band": None,
            "monthly_payment_cents": None,
            "missing_documents": [],
            "created_at": now,
            "updated_at": now,
        },
        "deal_umbrella_001": {
            "id": "deal_umbrella_001",
            "public_id": "D-2026-0003",
            "company_id": "cmp_umbrella_001",
            "partner_org_id": "org_partner_001",
            "client_org_id": None,
            "submitted_by_user_id": "user_partner_001",
            "status": "draft",
            "amount_cents": 6030000,
            "currency": "EUR",
            "duration_months": 36,
            "payment_frequency": "monthly",
            "category": "Laptops & Accessories",
            "risk_score": None,
            "risk_band": None,
            "monthly_payment_cents": None,
            "missing_documents": [],
            "created_at": now,
            "updated_at": now,
        },
    }

    quote_items_globex = [
        {
            "id": "qi_001",
            "label": "MacBook Pro 16",
            "category": "Laptops",
            "quantity": 26,
            "unit_price_cents": 249000,
            "total_price_cents": 26 * 249000,
        },
        {
            "id": "qi_002",
            "label": "Dell XPS 15",
            "category": "Laptops",
            "quantity": 3,
            "unit_price_cents": 215000,
            "total_price_cents": 3 * 215000,
        },
        {
            "id": "qi_003",
            "label": "iPhone 15 Pro",
            "category": "Phones",
            "quantity": 18,
            "unit_price_cents": 119000,
            "total_price_cents": 18 * 119000,
        },
        {
            "id": "qi_004",
            "label": "Monitor 27 4K",
            "category": "Monitors",
            "quantity": 24,
            "unit_price_cents": 45000,
            "total_price_cents": 24 * 45000,
        },
    ]

    quotes = {
        "quote_globex_001": {
            "id": "quote_globex_001",
            "deal_id": "deal_globex_001",
            "supplier_name": "Tech Distrib SAS",
            "quote_number": "TD-2026-1042",
            "amount_excl_tax_cents": 8550000,
            "amount_incl_tax_cents": int(8550000 * 1.20),
            "currency": "EUR",
            "category": "Laptops & Accessories",
            "extraction_status": "pending",
            "extraction_payload_json": {},
            "items": quote_items_globex,
            "created_at": now,
        },
    }

    documents: dict[str, Any] = {}
    risk_assessments: dict[str, Any] = {}
    pricing_proposals: dict[str, Any] = {}
    refi_packages: dict[str, Any] = {}
    financier_decisions: dict[str, Any] = {}
    offers: dict[str, Any] = {}
    contracts: dict[str, Any] = {}
    assets: dict[str, Any] = {}
    payment_schedules: dict[str, Any] = {}
    invoices: dict[str, Any] = {}
    payments: dict[str, Any] = {}
    tasks: dict[str, Any] = {}
    audit_events: list[dict] = []
    timeline_by_deal: dict[str, list[dict]] = {
        "deal_globex_001": [
            {"at": now, "type": "deal.created", "actor": "user_partner_001", "label": "Dossier créé"}
        ],
        "deal_acme_001": [
            {"at": now, "type": "deal.created", "actor": "user_partner_001", "label": "Dossier créé"}
        ],
        "deal_umbrella_001": [
            {"at": now, "type": "deal.created", "actor": "user_partner_001", "label": "Dossier créé"}
        ],
    }

    portfolio_history = _build_portfolio_history()

    return {
        "organizations": organizations,
        "users": users,
        "companies": companies,
        "deals": deals,
        "quotes": quotes,
        "documents": documents,
        "risk_assessments": risk_assessments,
        "pricing_proposals": pricing_proposals,
        "refi_packages": refi_packages,
        "financier_decisions": financier_decisions,
        "offers": offers,
        "contracts": contracts,
        "assets": assets,
        "payment_schedules": payment_schedules,
        "invoices": invoices,
        "payments": payments,
        "tasks": tasks,
        "audit_events": audit_events,
        "timeline_by_deal": timeline_by_deal,
        "portfolio_history": portfolio_history,
        "counters": {"deal_public": 3},
    }


def _build_portfolio_history() -> dict[str, Any]:
    today = date.today()
    months: list[dict[str, Any]] = []
    for i in range(11, -1, -1):
        m_year = today.year if today.month - i > 0 else today.year - 1
        m_month = today.month - i if today.month - i > 0 else today.month - i + 12
        months.append(
            {
                "month": f"{m_year:04d}-{m_month:02d}",
                "production_eur": 120000 + (i % 4) * 35000,
                "cash_collected_eur": 95000 + (i % 5) * 22000,
                "late_payments": (i % 3),
            }
        )
    return {
        "active_leases": 12,
        "total_commitment_eur": 2_450_000,
        "cash_collected_month_eur": 186_000,
        "cash_collected_ytd_eur": 1_540_000,
        "late_payments": 2,
        "refi_approval_rate_pct": 78,
        "activation_rate_pct": 91,
        "renewal_rate_pct": 64,
        "exposure_by_partner": [
            {"partner": "Tech Solutions Partner", "amount_eur": 1_280_000, "deals": 8},
            {"partner": "NorthBridge IT", "amount_eur": 720_000, "deals": 3},
            {"partner": "Atlas Distrib", "amount_eur": 450_000, "deals": 2},
        ],
        "risk_distribution": [
            {"band": "A", "count": 6, "exposure_eur": 1_180_000},
            {"band": "B", "count": 4, "exposure_eur": 920_000},
            {"band": "C", "count": 2, "exposure_eur": 350_000},
            {"band": "D", "count": 0, "exposure_eur": 0},
        ],
        "monthly": months,
    }


# ---------------------------------------------------------------------------
# Public access
# ---------------------------------------------------------------------------

_state: dict[str, Any] = _build_seed()


def db() -> dict[str, Any]:
    """Return the live state dict. Use under `with state_lock():` for mutations."""
    return _state


def state_lock():
    return _lock


def reset() -> None:
    global _state
    with _lock:
        _state = _build_seed()


def find_user_by_email(email: str) -> dict | None:
    for user in _state["users"].values():
        if user["email"].lower() == email.lower():
            return user
    return None


def next_deal_public_id() -> str:
    with _lock:
        _state["counters"]["deal_public"] += 1
        n = _state["counters"]["deal_public"]
    year = datetime.now(timezone.utc).year
    return f"D-{year}-{n:04d}"


def append_timeline(deal_id: str, event_type: str, actor: str, label: str, **payload) -> None:
    with _lock:
        evt = {
            "at": _now_iso(),
            "type": event_type,
            "actor": actor,
            "label": label,
            "payload": payload,
        }
        _state["timeline_by_deal"].setdefault(deal_id, []).append(evt)
        _state["audit_events"].append(
            {
                "id": _new_id("evt"),
                "actor_user_id": actor,
                "entity_type": "deal",
                "entity_id": deal_id,
                "event_type": event_type,
                "payload_json": payload,
                "created_at": evt["at"],
            }
        )


def append_audit(entity_type: str, entity_id: str, event_type: str, actor: str, **payload) -> None:
    with _lock:
        _state["audit_events"].append(
            {
                "id": _new_id("evt"),
                "actor_user_id": actor,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "event_type": event_type,
                "payload_json": payload,
                "created_at": _now_iso(),
            }
        )


# Re-export utilities

now_iso = _now_iso
new_id = _new_id


def snapshot() -> dict[str, Any]:
    """Deep copy of state for debugging."""
    with _lock:
        return copy.deepcopy(_state)


def fake_latency() -> None:
    """Optional sleep to make demo feel real."""
    from app.core.config import settings as _settings

    if _settings.demo_latency_ms > 0:
        time.sleep(_settings.demo_latency_ms / 1000.0)
