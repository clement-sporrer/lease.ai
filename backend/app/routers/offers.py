from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends

from app._demo_auth import get_current_user_demo
from app.envelope import ok
from app.errors import APIError
from app.services.transitions import assert_deal_transition
from app.state import append_timeline, db, new_id, now_iso, state_lock

router = APIRouter()


@router.post("/deals/{deal_id}/offers", status_code=201)
def create_offer(
    deal_id: str,
    payload: dict[str, Any] | None = None,
    user: dict = Depends(get_current_user_demo),
) -> dict:
    deal = db()["deals"].get(deal_id)
    if not deal:
        raise APIError("ENTITY_NOT_FOUND", f"Deal {deal_id} not found", status=404)

    proposals = [p for p in db()["pricing_proposals"].values() if p["deal_id"] == deal_id]
    proposals.sort(key=lambda p: p.get("version", 0), reverse=True)
    pricing_proposal_id = proposals[0]["id"] if proposals else None

    offer_id = new_id("offer")
    doc_id = new_id("doc")
    valid_until = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(timespec="seconds")

    offer_doc = {
        "id": doc_id,
        "deal_id": deal_id,
        "type": "signed_offer",
        "status": "uploaded",
        "file_name": f"{deal['public_id']}_firm_offer.pdf",
        "storage_key": f"offers/{offer_id}/offer.pdf",
        "mime_type": "application/pdf",
        "size_bytes": 64000,
        "version": 1,
        "uploaded_by_user_id": user["user_id"],
        "validated_by_user_id": None,
        "created_at": now_iso(),
    }

    offer = {
        "id": offer_id,
        "deal_id": deal_id,
        "deal_public_id": deal["public_id"],
        "status": "draft",
        "pricing_proposal_id": pricing_proposal_id,
        "document_id": doc_id,
        "valid_until": valid_until,
        "amount_cents": deal["amount_cents"],
        "duration_months": deal["duration_months"],
        "monthly_payment_cents": deal.get("monthly_payment_cents"),
        "currency": "EUR",
        "created_at": now_iso(),
    }

    with state_lock():
        db()["offers"][offer_id] = offer
        db()["documents"][doc_id] = offer_doc
        if deal["status"] == "financier_approved":
            assert_deal_transition(deal["status"], "firm_offer_generated")
            deal["status"] = "firm_offer_generated"
            deal["updated_at"] = now_iso()

    append_timeline(deal_id, "offer.generated", user["user_id"], "Offre ferme générée")
    return ok(offer)


@router.get("/offers/{offer_id}")
def get_offer(offer_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    offer = db()["offers"].get(offer_id)
    if not offer:
        raise APIError("ENTITY_NOT_FOUND", "Offer not found", status=404)
    return ok(offer)


@router.post("/offers/{offer_id}/send")
def send_offer(offer_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    offer = db()["offers"].get(offer_id)
    if not offer:
        raise APIError("ENTITY_NOT_FOUND", "Offer not found", status=404)
    with state_lock():
        offer["status"] = "sent"
        offer["sent_at"] = now_iso()
    append_timeline(offer["deal_id"], "offer.sent", user["user_id"], "Offre envoyée")
    return ok(offer)
