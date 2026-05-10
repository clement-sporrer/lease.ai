import datetime

from app.schemas.pricing import IndicativePricingRequest, PricingProposalResponse


def compute_monthly_payment(
    amount_cents: int,
    duration_months: int,
    refi_rate: float = 0.045,
    margin_rate: float = 0.025,
    fees_cents: int = 50_000,
) -> int:
    r = (refi_rate + margin_rate) / 12
    if r == 0:
        base = amount_cents / duration_months
    else:
        base = amount_cents * r / (1 - (1 + r) ** -duration_months)
    monthly = base + fees_cents / duration_months
    return round(monthly)


def build_pricing_proposal(req: IndicativePricingRequest) -> PricingProposalResponse:
    monthly = compute_monthly_payment(
        amount_cents=req.amount_cents,
        duration_months=req.duration_months,
        refi_rate=req.refi_rate,
        margin_rate=req.margin_rate,
        fees_cents=req.fees_cents,
    )
    return PricingProposalResponse(
        type="indicative",
        amount_financed_cents=req.amount_cents,
        duration_months=req.duration_months,
        monthly_payment_cents=monthly,
        refi_rate=req.refi_rate,
        margin_rate=req.margin_rate,
        fees_cents=req.fees_cents,
        assumptions={
            "refi_rate": req.refi_rate,
            "margin_rate": req.margin_rate,
            "total_rate": req.refi_rate + req.margin_rate,
            "fees_cents": req.fees_cents,
            "computed_at": datetime.datetime.utcnow().isoformat(),
        },
        version=1,
    )
