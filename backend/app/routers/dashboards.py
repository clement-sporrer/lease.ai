from collections import Counter

from fastapi import APIRouter, Depends

from app._demo_auth import get_current_user_demo
from app.envelope import ok
from app.state import db

router = APIRouter()


@router.get("/dashboards/partner")
def partner_dashboard(user: dict = Depends(get_current_user_demo)) -> dict:
    deals = list(db()["deals"].values())
    active = [d for d in deals if d["status"] not in ("active", "cancelled", "financier_rejected", "closed")]
    approved = [d for d in deals if d["status"] in ("financier_approved", "firm_offer_generated", "contract_generated", "signing", "signed", "activation_pending", "active")]
    to_complete = [d for d in deals if d["status"] in ("draft", "missing_documents", "company_enriched", "quote_added")]
    total_engagement = sum(d["amount_cents"] for d in deals)
    estimated_commission = int(total_engagement * 0.03)

    return ok(
        {
            "kpis": {
                "active_deals": len(active),
                "total_engagement_cents": total_engagement,
                "deals_to_complete": len(to_complete),
                "deals_approved": len(approved),
                "estimated_commission_cents": estimated_commission,
            },
            "recent_activity": _recent_activity(),
        }
    )


@router.get("/dashboards/client")
def client_dashboard(user: dict = Depends(get_current_user_demo)) -> dict:
    contracts = [c for c in db()["contracts"].values() if c.get("status") in ("active", "in_repayment")]
    total = sum(c.get("total_commitment_cents", 0) for c in contracts)
    upcoming = [
        s for s in db()["payment_schedules"].values() if s["status"] == "upcoming"
    ]
    upcoming.sort(key=lambda s: s["due_date"])
    return ok(
        {
            "kpis": {
                "active_contracts": len(contracts),
                "total_commitment_cents": total,
                "next_payment": upcoming[0] if upcoming else None,
            },
            "contracts": contracts,
        }
    )


@router.get("/dashboards/admin")
def admin_dashboard(user: dict = Depends(get_current_user_demo)) -> dict:
    deals = list(db()["deals"].values())
    by_status = Counter(d["status"] for d in deals)
    open_tasks = [t for t in db()["tasks"].values() if t.get("status") == "open"]
    return ok(
        {
            "kpis": {
                "submitted": by_status.get("submitted", 0),
                "internal_review": by_status.get("internal_review", 0),
                "missing_documents": by_status.get("missing_documents", 0),
                "refi_review": by_status.get("refi_review", 0),
                "signing": by_status.get("signing", 0),
                "active": by_status.get("active", 0),
                "open_tasks": len(open_tasks),
            },
            "by_status": dict(by_status),
            "recent_activity": _recent_activity(),
        }
    )


@router.get("/dashboards/cfo/portfolio")
def cfo_portfolio(user: dict = Depends(get_current_user_demo)) -> dict:
    history = db()["portfolio_history"]
    deals = list(db()["deals"].values())
    contracts = list(db()["contracts"].values())

    live_active = sum(1 for c in contracts if c["status"] in ("active", "in_repayment"))
    return ok(
        {
            "production_month_eur": history["monthly"][-1]["production_eur"] if history["monthly"] else 0,
            "active_leases": history["active_leases"] + live_active,
            "total_commitment_eur": history["total_commitment_eur"]
            + sum(c.get("total_commitment_cents", 0) for c in contracts) / 100,
            "cash_collected_month_eur": history["cash_collected_month_eur"],
            "late_payments": history["late_payments"],
            "refi_approval_rate_pct": history["refi_approval_rate_pct"],
            "activation_rate_pct": history["activation_rate_pct"],
            "renewal_rate_pct": history["renewal_rate_pct"],
            "exposure_by_partner": history["exposure_by_partner"],
            "monthly": history["monthly"],
            "open_deals": len([d for d in deals if d["status"] not in ("active", "cancelled", "closed", "financier_rejected")]),
        }
    )


@router.get("/dashboards/cfo/cash")
def cfo_cash(user: dict = Depends(get_current_user_demo)) -> dict:
    history = db()["portfolio_history"]
    upcoming = [
        s for s in db()["payment_schedules"].values() if s["status"] in ("upcoming", "invoiced")
    ]
    upcoming_total = sum(s["amount_cents"] for s in upcoming)
    received = sum(p["amount_cents"] for p in db()["payments"].values() if p["status"] == "received")

    return ok(
        {
            "cash_collected_month_eur": history["cash_collected_month_eur"],
            "cash_collected_ytd_eur": history["cash_collected_ytd_eur"],
            "expected_next_30d_cents": upcoming_total,
            "received_cents": received,
            "monthly": history["monthly"],
            "late_payments": history["late_payments"],
        }
    )


@router.get("/dashboards/cfo/risk")
def cfo_risk(user: dict = Depends(get_current_user_demo)) -> dict:
    history = db()["portfolio_history"]
    deals = list(db()["deals"].values())
    by_band = Counter(d.get("risk_band") for d in deals if d.get("risk_band"))
    return ok(
        {
            "distribution": history["risk_distribution"],
            "live_band_distribution": dict(by_band),
            "exposure_by_partner": history["exposure_by_partner"],
        }
    )


def _recent_activity(limit: int = 8) -> list[dict]:
    items: list[dict] = []
    for events in db()["timeline_by_deal"].values():
        items.extend(events)
    items.sort(key=lambda e: e["at"], reverse=True)
    return items[:limit]
