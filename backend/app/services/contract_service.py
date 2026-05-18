# backend/app/services/contract_service.py
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.contract import Asset, Contract, PaymentSchedule
from app.models.offer import Offer
from app.models.pricing_proposal import PricingProposal
from app.models.quote import Quote, QuoteItem
from app.models.refi_package import FinancierDecision, RefiPackage
from app.services import deal_service
from dateutil.relativedelta import relativedelta

_GENERATE_ALLOWED = {"firm_offer_generated", "contract_generated", "signing", "signed"}


async def _get_latest_contract(db: AsyncSession, deal_id: uuid.UUID) -> Contract | None:
    result = await db.execute(
        select(Contract)
        .where(Contract.deal_id == deal_id)
        .order_by(Contract.created_at.desc())
    )
    return result.scalar_one_or_none()


async def get_contract(db: AsyncSession, contract_id: uuid.UUID) -> Contract:
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if contract is None:
        raise AppError(404, "CONTRACT_NOT_FOUND", f"Contract {contract_id} not found")
    return contract


async def generate_contract(db: AsyncSession, deal_id: uuid.UUID, user_id: str) -> Contract:
    deal = await deal_service.get_deal(db, deal_id)
    if deal.status not in _GENERATE_ALLOWED:
        raise AppError(
            409,
            "INVALID_STATE",
            f"Cannot generate contract from status {deal.status!r}",
            {"current_status": deal.status, "allowed": sorted(_GENERATE_ALLOWED)},
        )
    existing = await _get_latest_contract(db, deal_id)
    if existing is not None:
        return existing

    public_id = f"CTR-{deal.public_id}"
    contract = Contract(
        id=uuid.uuid4(),
        deal_id=deal_id,
        public_id=public_id,
        status="draft",
    )
    db.add(contract)
    if deal.status == "firm_offer_generated":
        await deal_service.transition_deal(db, deal_id, "contract_generated")
    await db.commit()
    await db.refresh(contract)
    return contract


async def send_signature(db: AsyncSession, contract_id: uuid.UUID, user_id: str) -> Contract:
    contract = await get_contract(db, contract_id)
    if contract.status != "draft":
        raise AppError(
            409,
            "INVALID_STATE",
            f"Contract status is {contract.status!r}, must be draft to send for signature",
        )
    contract.sent_at = datetime.now(timezone.utc)
    contract.status = "sent_for_signature"
    await deal_service.transition_deal(db, contract.deal_id, "signing")
    await db.commit()
    await db.refresh(contract)
    return contract


async def mock_sign(db: AsyncSession, contract_id: uuid.UUID, user_id: str) -> Contract:
    contract = await get_contract(db, contract_id)
    if contract.status != "sent_for_signature":
        raise AppError(
            409,
            "INVALID_STATE",
            f"Contract status is {contract.status!r}, must be sent_for_signature to sign",
        )
    contract.signed_at = datetime.now(timezone.utc)
    contract.status = "signed"
    await deal_service.transition_deal(db, contract.deal_id, "signed")
    await db.commit()
    await db.refresh(contract)
    return contract


async def _check_financier_decision(db: AsyncSession, deal_id: uuid.UUID) -> bool:
    pkg_result = await db.execute(
        select(RefiPackage).where(RefiPackage.deal_id == deal_id).order_by(RefiPackage.created_at.desc())
    )
    pkg = pkg_result.scalar_one_or_none()
    if pkg is None:
        return False
    dec_result = await db.execute(
        select(FinancierDecision).where(
            FinancierDecision.refi_package_id == pkg.id,
            FinancierDecision.decision == "approved",
        )
    )
    return dec_result.scalar_one_or_none() is not None


async def _check_active_offer(db: AsyncSession, deal_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Offer).where(Offer.deal_id == deal_id, Offer.is_active.is_(True))
    )
    return result.scalar_one_or_none() is not None


async def _check_quote_validated(db: AsyncSession, deal_id: uuid.UUID) -> bool:
    result = await db.execute(
        select(Quote).where(
            Quote.deal_id == deal_id,
            Quote.extraction_status == "validated",
        )
    )
    return result.scalar_one_or_none() is not None


async def activation_checklist(db: AsyncSession, contract_id: uuid.UUID) -> dict:
    contract = await get_contract(db, contract_id)

    financier_ok = await _check_financier_decision(db, contract.deal_id)
    offer_ok = await _check_active_offer(db, contract.deal_id)
    quote_ok = await _check_quote_validated(db, contract.deal_id)

    items = [
        {"key": "contract_generated", "label": "Contrat généré", "satisfied": True},
        {"key": "contract_sent", "label": "Contrat envoyé pour signature", "satisfied": contract.sent_at is not None},
        {"key": "contract_signed", "label": "Contrat signé", "satisfied": contract.signed_at is not None},
        {"key": "financier_decision_received", "label": "Accord financeur reçu", "satisfied": financier_ok},
        {"key": "active_offer_present", "label": "Offre ferme active", "satisfied": offer_ok},
        {"key": "quote_validated", "label": "Devis validé", "satisfied": quote_ok},
    ]
    all_satisfied = all(item["satisfied"] for item in items)
    return {"items": items, "all_satisfied": all_satisfied}


async def activate(db: AsyncSession, contract_id: uuid.UUID, user_id: str) -> Contract:
    contract = await get_contract(db, contract_id)

    checklist = await activation_checklist(db, contract_id)
    if not checklist["all_satisfied"]:
        failed = [item["key"] for item in checklist["items"] if not item["satisfied"]]
        raise AppError(
            400,
            "ACTIVATION_BLOCKED",
            "Activation blocked: not all conditions are satisfied",
            {"failed_conditions": failed},
        )

    pricing_result = await db.execute(
        select(PricingProposal)
        .where(PricingProposal.deal_id == contract.deal_id)
        .order_by(PricingProposal.version.desc())
    )
    pricing = pricing_result.scalar_one_or_none()
    if pricing is None:
        raise AppError(
            409,
            "PRICING_PROPOSAL_MISSING",
            "No pricing proposal found for this deal — cannot generate payment schedule",
        )

    quote_result = await db.execute(
        select(Quote)
        .where(Quote.deal_id == contract.deal_id)
        .order_by(Quote.created_at.desc())
    )
    quote = quote_result.scalar_one_or_none()

    if quote is None:
        raise AppError(
            409,
            "QUOTE_MISSING",
            "No quote found for this deal — cannot create assets",
        )
    items_result = await db.execute(
        select(QuoteItem).where(QuoteItem.quote_id == quote.id)
    )
    quote_items = list(items_result.scalars().all())
    for item in quote_items:
        asset = Asset(
            id=uuid.uuid4(),
            contract_id=contract.id,
            name=item.label,
            category=item.category,
            quantity=item.quantity,
            unit_value_cents=item.unit_price_cents,
        )
        db.add(asset)

    now = datetime.now(timezone.utc)
    for n in range(1, pricing.duration_months + 1):
        schedule_entry = PaymentSchedule(
            id=uuid.uuid4(),
            contract_id=contract.id,
            due_date=now + relativedelta(months=n),
            amount_cents=pricing.monthly_payment_cents,
            status="pending",
        )
        db.add(schedule_entry)

    contract.total_commitment_cents = pricing.monthly_payment_cents * pricing.duration_months
    contract.activated_at = now
    contract.status = "active"

    # transition_deal commits internally; second call sees the updated status
    await deal_service.transition_deal(db, contract.deal_id, "activation_pending")
    await deal_service.transition_deal(db, contract.deal_id, "active")

    await db.commit()
    await db.refresh(contract)
    return contract
