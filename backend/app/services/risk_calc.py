"""Rule-based risk scoring per docs/flows/risk_rules.md.

Returns score 0-100, band A-E, flags list, rules_applied list, recommendation.
"""
from __future__ import annotations

from datetime import date


def _company_age_years(creation_date_str: str | None) -> float:
    if not creation_date_str:
        return 0.0
    try:
        d = date.fromisoformat(creation_date_str)
    except ValueError:
        return 0.0
    today = date.today()
    return (today - d).days / 365.25


def _band(score: int) -> str:
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    if score >= 30:
        return "D"
    return "E"


def assess(*, company: dict, deal: dict, partner_quality: str = "A", documents_ok: bool = True) -> dict:
    score = 50
    flags: list[str] = []
    rules: list[str] = []

    if not company.get("active_status"):
        flags.append("company_inactive")
        rules.append("inactive: auto_reject")
        return {
            "score": 0,
            "band": "E",
            "flags": flags,
            "rules_applied": rules,
            "recommendation": "auto_reject",
            "auto_reject": True,
        }

    score += 15
    rules.append("company_active +15")

    age = _company_age_years(company.get("creation_date"))
    if age > 3:
        score += 15
        rules.append(f"age_{age:.1f}y>3 +15")
    elif age < 1:
        score -= 15
        flags.append("company_too_young")
        rules.append(f"age_{age:.1f}y<1 -15")

    amount_eur = deal.get("amount_cents", 0) / 100
    if amount_eur < 25_000:
        score += 10
        rules.append("amount<25k +10")
    if amount_eur > 50_000:
        flags.append("large_ticket")
        rules.append("amount>50k flag")

    category = (deal.get("category") or "").lower()
    if any(k in category for k in ("laptop", "phone", "monitor", "network")):
        score += 10
        rules.append("standard_asset +10")
    else:
        score -= 10
        flags.append("non_standard_asset")
        rules.append("non_standard_asset -10")

    if partner_quality in ("A", "B"):
        score += 10
        rules.append(f"partner_{partner_quality} +10")

    if documents_ok:
        score += 10
        rules.append("docs_min_present +10")

    if not flags:
        score += 10
        rules.append("no_major_flag +10")

    score = max(0, min(100, score))
    band = _band(score)

    if band in ("A", "B") and documents_ok:
        recommendation = "internal_pre_approval_possible"
    elif band == "C":
        recommendation = "risk_review"
    elif band == "D":
        recommendation = "senior_review_or_reject"
    else:
        recommendation = "likely_reject"

    return {
        "score": score,
        "band": band,
        "flags": flags,
        "rules_applied": rules,
        "recommendation": recommendation,
        "auto_reject": False,
    }
