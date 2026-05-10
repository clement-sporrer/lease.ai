from typing import Any

from fastapi import APIRouter, Depends, Query

from app._demo_auth import get_current_user_demo
from app.envelope import ok, page
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


@router.post("/deals/{deal_id}/refi-package", status_code=201)
def generate_package(
    deal_id: str,
    payload: dict[str, Any] | None = None,
    user: dict = Depends(get_current_user_demo),
) -> dict:
    deal = db()["deals"].get(deal_id)
    if not deal:
        raise APIError("ENTITY_NOT_FOUND", f"Deal {deal_id} not found", status=404)

    fake_latency()
    payload = payload or {}
    financier_org_id = payload.get("financier_org_id", "org_financier_001")

    pkg_id = new_id("pkg")
    pdf_doc_id = new_id("doc")
    pdf_doc = {
        "id": pdf_doc_id,
        "deal_id": deal_id,
        "type": "refi_package",
        "status": "validated",
        "file_name": f"{deal['public_id']}_refi_package.pdf",
        "storage_key": f"refi-packages/{pkg_id}/package.pdf",
        "mime_type": "application/pdf",
        "size_bytes": 86000,
        "version": 1,
        "uploaded_by_user_id": user["user_id"],
        "validated_by_user_id": user["user_id"],
        "created_at": now_iso(),
    }

    package = {
        "id": pkg_id,
        "deal_id": deal_id,
        "deal_public_id": deal["public_id"],
        "status": "ready",
        "financier_org_id": financier_org_id,
        "pdf_document_id": pdf_doc_id,
        "zip_document_id": None,
        "summary": {
            "client": db()["companies"].get(deal.get("company_id") or "", {}).get("legal_name", "Unknown"),
            "amount_financed_cents": deal["amount_cents"],
            "duration_months": deal["duration_months"],
            "monthly_payment_cents": deal.get("monthly_payment_cents"),
            "risk_score": deal.get("risk_score"),
            "risk_band": deal.get("risk_band"),
        },
        "generated_at": now_iso(),
        "sent_at": None,
        "decision_at": None,
    }

    with state_lock():
        db()["refi_packages"][pkg_id] = package
        db()["documents"][pdf_doc_id] = pdf_doc
        if deal["status"] == "pre_approved":
            assert_deal_transition(deal["status"], "refi_package_ready")
            deal["status"] = "refi_package_ready"
        deal["updated_at"] = now_iso()

    append_timeline(deal_id, "refi_package.generated", user["user_id"], "Package financeur généré")
    return ok(package)


@router.get("/refi-packages")
def list_packages(
    status: str | None = Query(None),
    financier_org_id: str | None = Query(None),
    user: dict = Depends(get_current_user_demo),
) -> dict:
    pkgs = list(db()["refi_packages"].values())
    role = user.get("active_role")
    role_str = role.value if hasattr(role, "value") else str(role)
    if role_str == "financier":
        pkgs = [p for p in pkgs if p.get("financier_org_id") == user.get("organization_id") or True]
    if status:
        pkgs = [p for p in pkgs if p["status"] == status]
    if financier_org_id:
        pkgs = [p for p in pkgs if p.get("financier_org_id") == financier_org_id]
    pkgs.sort(key=lambda p: p["generated_at"], reverse=True)
    return page(pkgs, 1, len(pkgs), len(pkgs))


@router.get("/refi-packages/{package_id}")
def get_package(package_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    pkg = db()["refi_packages"].get(package_id)
    if not pkg:
        raise APIError("ENTITY_NOT_FOUND", "Package not found", status=404)
    return ok(pkg)


@router.get("/refi-packages/{package_id}/download-url")
def package_download(package_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    pkg = db()["refi_packages"].get(package_id)
    if not pkg:
        raise APIError("ENTITY_NOT_FOUND", "Package not found", status=404)
    return ok({"url": "/static/refi_demo.pdf", "expires_in_seconds": 300, "package_id": package_id})


@router.post("/refi-packages/{package_id}/send")
def send_package(package_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    pkg = db()["refi_packages"].get(package_id)
    if not pkg:
        raise APIError("ENTITY_NOT_FOUND", "Package not found", status=404)
    deal = db()["deals"].get(pkg["deal_id"])
    with state_lock():
        pkg["status"] = "sent"
        pkg["sent_at"] = now_iso()
        if deal and deal["status"] == "refi_package_ready":
            assert_deal_transition(deal["status"], "refi_review")
            deal["status"] = "refi_review"
            deal["updated_at"] = now_iso()
    append_timeline(pkg["deal_id"], "refi_package.sent", user["user_id"], "Package envoyé au financeur")
    return ok(pkg)


@router.post("/refi-packages/{package_id}/decision")
def package_decision(
    package_id: str, payload: dict[str, Any], user: dict = Depends(get_current_user_demo)
) -> dict:
    pkg = db()["refi_packages"].get(package_id)
    if not pkg:
        raise APIError("ENTITY_NOT_FOUND", "Package not found", status=404)

    decision = payload.get("decision")
    if decision not in ("approved", "rejected", "clarification_requested"):
        raise APIError(
            "VALIDATION_ERROR",
            "decision must be approved, rejected, or clarification_requested",
            status=422,
        )
    comment = payload.get("comment", "")

    decision_id = new_id("dec")
    record = {
        "id": decision_id,
        "refi_package_id": package_id,
        "decision": decision,
        "comment": comment,
        "decided_by_user_id": user["user_id"],
        "decided_at": now_iso(),
    }

    deal = db()["deals"].get(pkg["deal_id"])
    with state_lock():
        db()["financier_decisions"][decision_id] = record
        pkg["status"] = decision
        pkg["decision_at"] = now_iso()

        if deal and deal["status"] in ("refi_review", "refi_package_ready"):
            if decision == "approved":
                if deal["status"] != "refi_review":
                    deal["status"] = "refi_review"
                assert_deal_transition(deal["status"], "financier_approved")
                deal["status"] = "financier_approved"
            elif decision == "rejected":
                if deal["status"] != "refi_review":
                    deal["status"] = "refi_review"
                assert_deal_transition(deal["status"], "financier_rejected")
                deal["status"] = "financier_rejected"
            elif decision == "clarification_requested":
                if deal["status"] != "refi_review":
                    deal["status"] = "refi_review"
                assert_deal_transition(deal["status"], "missing_documents")
                deal["status"] = "missing_documents"
            deal["updated_at"] = now_iso()

    append_timeline(
        pkg["deal_id"],
        f"financier.{decision}",
        user["user_id"],
        f"Décision financeur: {decision}",
        comment=comment,
    )
    return ok(record)
