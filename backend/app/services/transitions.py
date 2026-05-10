"""Status machine guard per docs/backend/status_machine.md."""
from __future__ import annotations

from app.errors import APIError

DEAL_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["company_enriched", "cancelled"],
    "company_enriched": ["quote_added", "cancelled"],
    "quote_added": ["indicative_offer_ready", "cancelled"],
    "indicative_offer_ready": ["submitted", "cancelled"],
    "submitted": ["internal_review"],
    "internal_review": ["missing_documents", "pre_approved", "financier_rejected"],
    "missing_documents": ["internal_review", "cancelled"],
    "pre_approved": ["refi_package_ready"],
    "refi_package_ready": ["refi_review"],
    "refi_review": ["financier_approved", "financier_rejected", "missing_documents"],
    "financier_approved": ["firm_offer_generated"],
    "firm_offer_generated": ["contract_generated"],
    "contract_generated": ["signing"],
    "signing": ["signed"],
    "signed": ["activation_pending"],
    "activation_pending": ["active"],
    "active": [],
    "cancelled": [],
    "financier_rejected": ["cancelled"],
}

CONTRACT_TRANSITIONS: dict[str, list[str]] = {
    "draft": ["generated", "cancelled"],
    "generated": ["sent_for_signature", "cancelled"],
    "sent_for_signature": ["signed", "cancelled"],
    "signed": ["activation_pending"],
    "activation_pending": ["active"],
    "active": ["in_repayment", "closed"],
    "in_repayment": ["renewal_window", "closed", "defaulted"],
    "renewal_window": ["closed", "active"],
    "closed": [],
    "defaulted": ["closed"],
    "cancelled": [],
}


def assert_deal_transition(current: str, target: str) -> None:
    allowed = DEAL_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise APIError(
            "DEAL_INVALID_TRANSITION",
            f"Transition {current} -> {target} not allowed",
            status=409,
            details={"current_status": current, "allowed_statuses": allowed, "target": target},
        )


def assert_contract_transition(current: str, target: str) -> None:
    allowed = CONTRACT_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise APIError(
            "CONTRACT_INVALID_TRANSITION",
            f"Transition {current} -> {target} not allowed",
            status=409,
            details={"current_status": current, "allowed_statuses": allowed, "target": target},
        )
