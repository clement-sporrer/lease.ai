from datetime import date, timedelta

from app.services.risk_service import RISKY_NAF_CODES, assess_risk


def _age(years: float) -> date:
    return date.today() - timedelta(days=int(years * 365))


def test_default_score_is_75_green():
    result = assess_risk(
        creation_date=_age(5),
        amount_cents=5_000_000,
        activity_code="6201Z",
        is_active=True,
    )
    assert result["score"] == 75
    assert result["band"] == "green"


def test_recent_company_penalty():
    result = assess_risk(
        creation_date=_age(1),
        amount_cents=5_000_000,
        activity_code="6201Z",
        is_active=True,
    )
    assert result["score"] == 45
    assert result["band"] == "orange"
    assert "recent_company" in result["flags"]


def test_high_amount_penalty():
    result = assess_risk(
        creation_date=_age(5),
        amount_cents=15_000_000,
        activity_code="6201Z",
        is_active=True,
    )
    assert result["score"] == 65
    assert result["band"] == "green"
    assert "high_amount" in result["flags"]


def test_risky_sector_penalty():
    risky_code = next(iter(RISKY_NAF_CODES))
    result = assess_risk(
        creation_date=_age(5),
        amount_cents=5_000_000,
        activity_code=risky_code,
        is_active=True,
    )
    assert result["score"] == 60
    assert "risky_sector" in result["flags"]


def test_inactive_company_penalty():
    result = assess_risk(
        creation_date=_age(5),
        amount_cents=5_000_000,
        activity_code="6201Z",
        is_active=False,
    )
    assert result["score"] == 25
    assert result["band"] == "red"
    assert "company_inactive" in result["flags"]


def test_combined_penalties_floor_at_zero():
    risky_code = next(iter(RISKY_NAF_CODES))
    result = assess_risk(
        creation_date=_age(0.5),
        amount_cents=15_000_000,
        activity_code=risky_code,
        is_active=False,
    )
    assert result["score"] == 0
    assert result["band"] == "red"


def test_none_activity_code_no_penalty():
    result = assess_risk(
        creation_date=_age(5),
        amount_cents=5_000_000,
        activity_code=None,
        is_active=True,
    )
    assert result["score"] == 75
