from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query

from app._demo_auth import get_current_user_demo
from app.envelope import ok
from app.errors import APIError
from app.state import (
    append_audit,
    append_timeline,
    db,
    new_id,
    now_iso,
    state_lock,
)

router = APIRouter()


def _next_invoice_number() -> str:
    n = len(db()["invoices"]) + 1
    return f"INV-{date.today().year}-{n:04d}"


@router.get("/contracts/{contract_id}/schedule")
def get_schedule(contract_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    if contract_id not in db()["contracts"]:
        raise APIError("ENTITY_NOT_FOUND", "Contract not found", status=404)
    items = [s for s in db()["payment_schedules"].values() if s["contract_id"] == contract_id]
    items.sort(key=lambda s: s["due_date"])
    return ok(items)


@router.post("/contracts/{contract_id}/schedule/generate")
def generate_schedule(
    contract_id: str,
    payload: dict[str, Any] | None = None,
    user: dict = Depends(get_current_user_demo),
) -> dict:
    contract = db()["contracts"].get(contract_id)
    if not contract:
        raise APIError("ENTITY_NOT_FOUND", "Contract not found", status=404)

    existing = [s for s in db()["payment_schedules"].values() if s["contract_id"] == contract_id]
    if existing:
        return ok(existing)

    monthly = contract.get("monthly_payment_cents") or 0
    months = contract.get("duration_months") or 36
    start = date.today()
    schedule = []
    with state_lock():
        for i in range(months):
            y = start.year + ((start.month - 1 + i) // 12)
            m = ((start.month - 1 + i) % 12) + 1
            due = date(y, m, min(start.day, 28))
            sid = new_id("sch")
            entry = {
                "id": sid,
                "contract_id": contract_id,
                "due_date": due.isoformat(),
                "amount_cents": monthly,
                "currency": "EUR",
                "status": "upcoming",
                "invoice_id": None,
                "payment_id": None,
                "period_index": i + 1,
            }
            db()["payment_schedules"][sid] = entry
            schedule.append(entry)
    append_timeline(contract["deal_id"], "schedule.generated", user["user_id"], "Échéancier généré")
    return ok(schedule)


@router.get("/contracts/{contract_id}/invoices")
def list_invoices(contract_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    if contract_id not in db()["contracts"]:
        raise APIError("ENTITY_NOT_FOUND", "Contract not found", status=404)
    items = [i for i in db()["invoices"].values() if i["contract_id"] == contract_id]
    items.sort(key=lambda i: i["issue_date"])
    return ok(items)


@router.post("/contracts/{contract_id}/invoices", status_code=201)
def create_invoice(
    contract_id: str,
    payload: dict[str, Any] | None = None,
    user: dict = Depends(get_current_user_demo),
) -> dict:
    contract = db()["contracts"].get(contract_id)
    if not contract:
        raise APIError("ENTITY_NOT_FOUND", "Contract not found", status=404)
    payload = payload or {}

    schedule_id = payload.get("schedule_id")
    schedule = db()["payment_schedules"].get(schedule_id) if schedule_id else None
    if not schedule:
        # First upcoming
        upcoming = [
            s for s in db()["payment_schedules"].values()
            if s["contract_id"] == contract_id and s["status"] == "upcoming"
        ]
        upcoming.sort(key=lambda s: s["due_date"])
        schedule = upcoming[0] if upcoming else None

    amount_cents = (schedule["amount_cents"] if schedule else contract.get("monthly_payment_cents") or 0)
    vat_cents = int(amount_cents * 0.20)
    issue = date.today()
    due = (issue + timedelta(days=15)) if not schedule else date.fromisoformat(schedule["due_date"])

    inv_id = new_id("inv")
    doc_id = new_id("doc")
    invoice_doc = {
        "id": doc_id,
        "deal_id": contract["deal_id"],
        "contract_id": contract_id,
        "type": "customer_invoice",
        "status": "validated",
        "file_name": f"{contract['public_id']}_{inv_id[-6:]}.pdf",
        "storage_key": f"invoices/{inv_id}/invoice.pdf",
        "mime_type": "application/pdf",
        "size_bytes": 42000,
        "version": 1,
        "uploaded_by_user_id": user["user_id"],
        "validated_by_user_id": user["user_id"],
        "created_at": now_iso(),
    }

    invoice = {
        "id": inv_id,
        "contract_id": contract_id,
        "invoice_number": _next_invoice_number(),
        "issue_date": issue.isoformat(),
        "due_date": due.isoformat(),
        "amount_cents": amount_cents,
        "vat_cents": vat_cents,
        "amount_incl_tax_cents": amount_cents + vat_cents,
        "status": "issued",
        "pdf_document_id": doc_id,
        "schedule_id": schedule["id"] if schedule else None,
    }

    with state_lock():
        db()["invoices"][inv_id] = invoice
        db()["documents"][doc_id] = invoice_doc
        if schedule:
            schedule["invoice_id"] = inv_id
            schedule["status"] = "invoiced"

    append_timeline(contract["deal_id"], "invoice.generated", user["user_id"], f"Facture {invoice['invoice_number']} émise")
    return ok(invoice)


@router.get("/invoices/{invoice_id}")
def get_invoice(invoice_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    inv = db()["invoices"].get(invoice_id)
    if not inv:
        raise APIError("ENTITY_NOT_FOUND", "Invoice not found", status=404)
    return ok(inv)


@router.get("/invoices/{invoice_id}/download-url")
def invoice_url(invoice_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    inv = db()["invoices"].get(invoice_id)
    if not inv:
        raise APIError("ENTITY_NOT_FOUND", "Invoice not found", status=404)
    return ok({"url": "/static/invoice_demo.pdf", "expires_in_seconds": 300, "invoice_id": invoice_id})


@router.post("/invoices/{invoice_id}/mark-sent")
def mark_invoice_sent(invoice_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    inv = db()["invoices"].get(invoice_id)
    if not inv:
        raise APIError("ENTITY_NOT_FOUND", "Invoice not found", status=404)
    with state_lock():
        inv["status"] = "sent"
        inv["sent_at"] = now_iso()
    append_audit("invoice", invoice_id, "invoice.sent", user["user_id"])
    return ok(inv)


@router.post("/invoices/{invoice_id}/mark-paid")
def mark_invoice_paid(
    invoice_id: str, payload: dict[str, Any] | None = None, user: dict = Depends(get_current_user_demo)
) -> dict:
    inv = db()["invoices"].get(invoice_id)
    if not inv:
        raise APIError("ENTITY_NOT_FOUND", "Invoice not found", status=404)
    payload = payload or {}

    payment_id = new_id("pay")
    payment = {
        "id": payment_id,
        "contract_id": inv["contract_id"],
        "invoice_id": invoice_id,
        "amount_cents": inv["amount_cents"] + inv.get("vat_cents", 0),
        "received_at": now_iso(),
        "method": payload.get("method", "sepa"),
        "status": "received",
        "reference": payload.get("reference", f"REF-{payment_id[-6:]}"),
    }

    with state_lock():
        db()["payments"][payment_id] = payment
        inv["status"] = "paid"
        inv["paid_at"] = now_iso()
        sched = db()["payment_schedules"].get(inv.get("schedule_id") or "")
        if sched:
            sched["status"] = "paid"
            sched["payment_id"] = payment_id

    contract = db()["contracts"].get(inv["contract_id"])
    if contract:
        append_timeline(
            contract["deal_id"],
            "payment.received",
            user["user_id"],
            f"Paiement reçu {payment['amount_cents'] / 100:.2f} EUR",
        )
    append_audit("payment", payment_id, "payment.received", user["user_id"])
    return ok({"invoice": inv, "payment": payment})


@router.get("/payments")
def list_payments(
    contract_id: str | None = Query(None),
    user: dict = Depends(get_current_user_demo),
) -> dict:
    items = list(db()["payments"].values())
    if contract_id:
        items = [p for p in items if p["contract_id"] == contract_id]
    items.sort(key=lambda p: p["received_at"], reverse=True)
    return ok(items)


@router.post("/payments", status_code=201)
def create_payment(
    payload: dict[str, Any], user: dict = Depends(get_current_user_demo)
) -> dict:
    invoice_id = payload.get("invoice_id")
    if not invoice_id or invoice_id not in db()["invoices"]:
        raise APIError("ENTITY_NOT_FOUND", "Invoice not found", status=404)
    return mark_invoice_paid(invoice_id, payload, user)
