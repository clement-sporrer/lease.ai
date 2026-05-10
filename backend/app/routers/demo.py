"""Demo control endpoints — reset state, inspect snapshot."""
from fastapi import APIRouter, Depends

from app._demo_auth import get_current_user_demo
from app.envelope import ok
from app.state import db, reset

router = APIRouter()


@router.post("/demo/reset")
def reset_state(user: dict = Depends(get_current_user_demo)) -> dict:
    reset()
    return ok({"message": "Demo state reset", "deals": len(db()["deals"])})


@router.get("/demo/snapshot")
def snapshot_state(user: dict = Depends(get_current_user_demo)) -> dict:
    s = db()
    counts = {
        "deals": len(s["deals"]),
        "companies": len(s["companies"]),
        "quotes": len(s["quotes"]),
        "documents": len(s["documents"]),
        "risk_assessments": len(s["risk_assessments"]),
        "pricing_proposals": len(s["pricing_proposals"]),
        "refi_packages": len(s["refi_packages"]),
        "offers": len(s["offers"]),
        "contracts": len(s["contracts"]),
        "assets": len(s["assets"]),
        "payment_schedules": len(s["payment_schedules"]),
        "invoices": len(s["invoices"]),
        "payments": len(s["payments"]),
        "audit_events": len(s["audit_events"]),
    }
    return ok({"counts": counts, "users": list(s["users"].keys())})


@router.get("/demo/users")
def list_demo_users(user: dict = Depends(get_current_user_demo)) -> dict:
    """Public demo users list for frontend role-switcher."""
    return ok(list(db()["users"].values()))
