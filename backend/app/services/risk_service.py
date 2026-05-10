from datetime import date

RISKY_NAF_CODES: frozenset[str] = frozenset(
    {
        "5610A",
        "5610B",
        "5630Z",
        "9200Z",
        "4711A",
        "4711B",
        "8010Z",
    }
)

_BAND_THRESHOLDS = (
    (60, "green"),
    (30, "orange"),
    (0, "red"),
)


def _band_for_score(score: int) -> str:
    for threshold, band in _BAND_THRESHOLDS:
        if score >= threshold:
            return band
    return "red"


def assess_risk(
    creation_date: date | None,
    amount_cents: int,
    activity_code: str | None,
    is_active: bool,
) -> dict[str, int | str | list[str]]:
    score = 75
    flags: list[str] = []
    rules_applied: list[str] = []

    if not is_active:
        score -= 50
        flags.append("company_inactive")
        rules_applied.append("inactive_company: -50")

    if creation_date is not None:
        age_years = (date.today() - creation_date).days / 365
        if age_years < 2:
            score -= 30
            flags.append("recent_company")
            rules_applied.append("company_age_lt_2y: -30")

    if amount_cents > 10_000_000:
        score -= 10
        flags.append("high_amount")
        rules_applied.append("amount_gt_100k: -10")

    if activity_code and activity_code in RISKY_NAF_CODES:
        score -= 15
        flags.append("risky_sector")
        rules_applied.append("risky_naf_code: -15")

    score = max(0, score)
    band = _band_for_score(score)

    recommendations = {
        "green": "Favorable profile.",
        "orange": "Profile requires monitoring.",
        "red": "High-risk profile.",
    }

    return {
        "score": score,
        "band": band,
        "flags": flags,
        "rules_applied": rules_applied,
        "recommendation": recommendations[band],
    }
