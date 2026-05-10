"""Pricing logic per docs/flows/pricing_logic.md.

Indicative monthly payment from amount, duration, score band, category.
All money in cents.
"""
from __future__ import annotations

REFI_RATE_BY_DURATION = {24: 0.045, 36: 0.050, 48: 0.055, 60: 0.060}
MARGIN_BY_BAND = {"A": 0.020, "B": 0.028, "C": 0.040, "D": 0.060}
RESIDUAL_RATE = {
    "Laptops": {24: 0.25, 36: 0.15, 48: 0.08, 60: 0.03},
    "Laptops & Accessories": {24: 0.25, 36: 0.15, 48: 0.08, 60: 0.03},
    "Phones": {24: 0.30, 36: 0.18, 48: 0.10, 60: 0.04},
    "Monitors": {24: 0.20, 36: 0.12, 48: 0.06, 60: 0.02},
    "Network": {24: 0.18, 36: 0.10, 48: 0.05, 60: 0.02},
    "Other": {24: 0.10, 36: 0.05, 48: 0.0, 60: 0.0},
}
SETUP_FEES_CENTS = 15000


def amortized_monthly_payment(principal_cents: int, annual_rate: float, months: int) -> int:
    if months <= 0:
        return principal_cents
    monthly_rate = annual_rate / 12.0
    if monthly_rate == 0:
        return principal_cents // months
    factor = (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    return int(round(principal_cents * factor))


def compute_indicative(
    *,
    amount_cents: int,
    duration_months: int,
    category: str,
    band: str = "B",
    setup_fees_cents: int = SETUP_FEES_CENTS,
) -> dict:
    duration = duration_months if duration_months in REFI_RATE_BY_DURATION else 36
    refi_rate = REFI_RATE_BY_DURATION[duration]
    margin = MARGIN_BY_BAND.get(band, MARGIN_BY_BAND["B"])
    residual_rate = RESIDUAL_RATE.get(category, RESIDUAL_RATE["Other"]).get(duration, 0.0)

    base_financed = amount_cents + setup_fees_cents
    residual_value_cents = int(amount_cents * residual_rate)
    amount_to_amortize = base_financed - residual_value_cents
    annual_rate = refi_rate + margin
    monthly = amortized_monthly_payment(amount_to_amortize, annual_rate, duration)

    return {
        "amount_financed_cents": base_financed,
        "duration_months": duration,
        "monthly_payment_cents": monthly,
        "residual_value_cents": residual_value_cents,
        "refi_rate": round(refi_rate, 4),
        "margin_rate": round(margin, 4),
        "fees_cents": setup_fees_cents,
        "assumptions": {
            "category": category,
            "band": band,
            "annual_rate_used": round(annual_rate, 4),
            "residual_rate": round(residual_rate, 4),
            "method": "amortized_constant_monthly",
        },
        "disclaimer": (
            "Mensualité indicative, sous réserve de validation du dossier, du financeur "
            "et des documents contractuels."
        ),
    }
