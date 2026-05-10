from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, Depends

from app._demo_auth import get_current_user_demo
from app.envelope import ok
from app.errors import APIError
from app.services.transitions import assert_deal_transition
from app.state import (
    append_timeline,
    db,
    fake_latency,
    new_id,
    now_iso,
    state_lock,
)

router = APIRouter()


def _generate_schedule(contract_id: str, start: date, months: int, monthly_cents: int) -> list[dict]:
    schedule = []
    for i in range(months):
        # naive month add
        y = start.year + ((start.month - 1 + i) // 12)
        m = ((start.month - 1 + i) % 12) + 1
        d = min(start.day, 28)
        due = date(y, m, d)
        schedule_id = new_id("sch")
        schedule.append(
            {
                "id": schedule_id,
                "contract_id": contract_id,
                "due_date": due.isoformat(),
                "amount_cents": monthly_cents,
                "currency": "EUR",
                "status": "upcoming",
                "invoice_id": None,
                "payment_id": None,
                "period_index": i + 1,
            }
        )
    return schedule


@router.post("/deals/{deal_id}/contracts", status_code=201)
def create_contract(
    deal_id: str,
    payload: dict[str, Any] | None = None,
    user: dict = Depends(get_current_user_demo),
) -> dict:
    deal = db()["deals"].get(deal_id)
    if not deal:
        raise APIError("ENTITY_NOT_FOUND", f"Deal {deal_id} not found", status=404)

    contract_id = new_id("contract")
    doc_id = new_id("doc")
    contract_doc = {
        "id": doc_id,
        "deal_id": deal_id,
        "contract_id": contract_id,
        "type": "contract",
        "status": "uploaded",
        "file_name": f"{deal['public_id']}_contract.pdf",
        "storage_key": f"contracts/{contract_id}/contract.pdf",
        "mime_type": "application/pdf",
        "size_bytes": 124000,
        "version": 1,
        "uploaded_by_user_id": user["user_id"],
        "validated_by_user_id": None,
        "created_at": now_iso(),
    }

    contract = {
        "id": contract_id,
        "public_id": deal["public_id"].replace("D-", "C-"),
        "deal_id": deal_id,
        "client_org_id": deal.get("client_org_id"),
        "status": "generated",
        "start_date": None,
        "end_date": None,
        "signed_at": None,
        "activated_at": None,
        "total_commitment_cents": (deal.get("monthly_payment_cents") or 0) * deal["duration_months"],
        "duration_months": deal["duration_months"],
        "monthly_payment_cents": deal.get("monthly_payment_cents"),
        "amount_cents": deal["amount_cents"],
        "document_id": doc_id,
        "created_at": now_iso(),
    }

    with state_lock():
        db()["contracts"][contract_id] = contract
        db()["documents"][doc_id] = contract_doc
        if deal["status"] == "firm_offer_generated":
            assert_deal_transition(deal["status"], "contract_generated")
            deal["status"] = "contract_generated"
            deal["updated_at"] = now_iso()

    append_timeline(deal_id, "contract.generated", user["user_id"], "Contrat généré")
    return ok(contract)


@router.get("/contracts/{contract_id}")
def get_contract(contract_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    c = db()["contracts"].get(contract_id)
    if not c:
        raise APIError("ENTITY_NOT_FOUND", "Contract not found", status=404)
    return ok(c)


@router.post("/contracts/{contract_id}/send-signature")
def send_signature(contract_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    c = db()["contracts"].get(contract_id)
    if not c:
        raise APIError("ENTITY_NOT_FOUND", "Contract not found", status=404)
    deal = db()["deals"].get(c["deal_id"])

    with state_lock():
        c["status"] = "sent_for_signature"
        c["signature_sent_at"] = now_iso()
        if deal and deal["status"] == "contract_generated":
            assert_deal_transition(deal["status"], "signing")
            deal["status"] = "signing"
            deal["updated_at"] = now_iso()
    append_timeline(c["deal_id"], "signature.started", user["user_id"], "Envoi signature")
    return ok(c)


@router.post("/contracts/{contract_id}/mock-sign")
def mock_sign(contract_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    c = db()["contracts"].get(contract_id)
    if not c:
        raise APIError("ENTITY_NOT_FOUND", "Contract not found", status=404)
    deal = db()["deals"].get(c["deal_id"])

    fake_latency()

    signed_doc_id = new_id("doc")
    signed_doc = {
        "id": signed_doc_id,
        "deal_id": c["deal_id"],
        "contract_id": contract_id,
        "type": "signed_contract",
        "status": "validated",
        "file_name": f"{c['public_id']}_signed.pdf",
        "storage_key": f"contracts/{contract_id}/signed.pdf",
        "mime_type": "application/pdf",
        "size_bytes": 138000,
        "version": 1,
        "uploaded_by_user_id": user["user_id"],
        "validated_by_user_id": user["user_id"],
        "created_at": now_iso(),
    }

    with state_lock():
        if c["status"] == "generated":
            c["status"] = "sent_for_signature"
        c["status"] = "signed"
        c["signed_at"] = now_iso()
        c["signed_document_id"] = signed_doc_id
        db()["documents"][signed_doc_id] = signed_doc

        if deal:
            if deal["status"] == "contract_generated":
                assert_deal_transition(deal["status"], "signing")
                deal["status"] = "signing"
            if deal["status"] == "signing":
                assert_deal_transition(deal["status"], "signed")
                deal["status"] = "signed"
            if deal["status"] == "signed":
                assert_deal_transition(deal["status"], "activation_pending")
                deal["status"] = "activation_pending"
            deal["updated_at"] = now_iso()

    append_timeline(c["deal_id"], "contract.signed", user["user_id"], "Contrat signé (mock)")
    return ok(c)


@router.get("/contracts/{contract_id}/activation-checklist")
def activation_checklist(contract_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    c = db()["contracts"].get(contract_id)
    if not c:
        raise APIError("ENTITY_NOT_FOUND", "Contract not found", status=404)
    docs = {d["type"]: d for d in db()["documents"].values() if d.get("contract_id") == contract_id or d.get("deal_id") == c["deal_id"]}
    has_assets = any(a.get("contract_id") == contract_id for a in db()["assets"].values())
    has_schedule = any(s.get("contract_id") == contract_id for s in db()["payment_schedules"].values())

    items = [
        {"code": "financier_approved", "status": "validated" if c.get("deal_id") and db()["deals"][c["deal_id"]]["status"] in ("activation_pending", "active", "signed") else "missing"},
        {"code": "firm_offer_generated", "status": "validated" if any(o["deal_id"] == c["deal_id"] for o in db()["offers"].values()) else "missing"},
        {"code": "contract_signed", "status": "validated" if c.get("signed_at") else "missing"},
        {"code": "sepa_mandate", "status": docs.get("sepa_mandate", {}).get("status", "missing") if "sepa_mandate" in docs else "missing"},
        {"code": "delivery_certificate", "status": docs.get("delivery_certificate", {}).get("status", "missing") if "delivery_certificate" in docs else "missing"},
        {"code": "asset_created", "status": "validated" if has_assets else "missing"},
        {"code": "schedule_generated", "status": "validated" if has_schedule else "missing"},
    ]
    blockers = [i for i in items if i["status"] != "validated"]
    return ok({"contract_id": contract_id, "items": items, "blockers": blockers, "ready": not blockers})


@router.post("/contracts/{contract_id}/activate")
def activate(contract_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    c = db()["contracts"].get(contract_id)
    if not c:
        raise APIError("ENTITY_NOT_FOUND", "Contract not found", status=404)
    deal = db()["deals"].get(c["deal_id"])

    if not c.get("signed_at"):
        raise APIError(
            "CONTRACT_ACTIVATION_BLOCKED",
            "Contract not signed",
            status=409,
            details={"missing": "signed_contract"},
        )

    today = date.today()
    monthly_cents = c.get("monthly_payment_cents") or 0
    months = c.get("duration_months") or 36

    has_schedule = any(s["contract_id"] == contract_id for s in db()["payment_schedules"].values())

    with state_lock():
        c["status"] = "active"
        c["activated_at"] = now_iso()
        c["start_date"] = today.isoformat()
        c["end_date"] = (today + timedelta(days=30 * months)).isoformat()

        if not has_schedule:
            for entry in _generate_schedule(contract_id, today, months, monthly_cents):
                db()["payment_schedules"][entry["id"]] = entry

        # Auto-create assets from quote items if none exist for this contract
        existing_assets = [a for a in db()["assets"].values() if a["contract_id"] == contract_id]
        if not existing_assets:
            quote = next(
                (q for q in db()["quotes"].values() if q["deal_id"] == c["deal_id"]),
                None,
            )
            if quote:
                for item in quote["items"]:
                    asset_id = new_id("asset")
                    db()["assets"][asset_id] = {
                        "id": asset_id,
                        "contract_id": contract_id,
                        "name": item["label"],
                        "category": item["category"],
                        "serial_number": None,
                        "quantity": item["quantity"],
                        "unit_value_cents": item["unit_price_cents"],
                        "residual_value_cents": int(item["unit_price_cents"] * 0.15),
                        "status": "active",
                    }

        if deal and deal["status"] == "activation_pending":
            assert_deal_transition(deal["status"], "active")
            deal["status"] = "active"
            deal["updated_at"] = now_iso()

    append_timeline(c["deal_id"], "contract.activated", user["user_id"], "Contrat actif")
    return ok(c)
