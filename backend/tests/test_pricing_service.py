import pytest
from app.services.pricing_service import compute_monthly_payment


def test_standard_annuity():
    # 100 000€ over 36 months, refi=4.5%, margin=2.5%, fees=500€
    # r = 0.07/12 = 0.005833...
    # monthly ≈ 100000 * 0.005833 / (1 - 1.005833^-36) ≈ 3087.69 + 13.88 fees = 3101.57
    result = compute_monthly_payment(
        amount_cents=10_000_000,
        duration_months=36,
        refi_rate=0.045,
        margin_rate=0.025,
        fees_cents=50_000,
    )
    assert 309_000 <= result <= 312_000  # ~3100€/month in cents


def test_zero_rate_uses_straight_line():
    result = compute_monthly_payment(
        amount_cents=12_000_000,
        duration_months=12,
        refi_rate=0.0,
        margin_rate=0.0,
        fees_cents=0,
    )
    assert result == 1_000_000  # 12000€ / 12 = 1000€


def test_fees_added_per_month():
    result_no_fees = compute_monthly_payment(
        amount_cents=10_000_000,
        duration_months=36,
        refi_rate=0.045,
        margin_rate=0.025,
        fees_cents=0,
    )
    result_with_fees = compute_monthly_payment(
        amount_cents=10_000_000,
        duration_months=36,
        refi_rate=0.045,
        margin_rate=0.025,
        fees_cents=36_000,  # 1€/month × 36
    )
    assert result_with_fees == result_no_fees + 1_000  # 36 000 / 36 = 1 000 cents


def test_short_duration():
    # 60 000€ over 6 months at 7% total — monthly ≈ 10 196€
    result = compute_monthly_payment(
        amount_cents=6_000_000,
        duration_months=6,
        refi_rate=0.045,
        margin_rate=0.025,
        fees_cents=0,
    )
    assert 1_018_000 <= result <= 1_022_000


def test_result_is_integer():
    result = compute_monthly_payment(
        amount_cents=10_000_001,
        duration_months=37,
        refi_rate=0.045,
        margin_rate=0.025,
        fees_cents=50_001,
    )
    assert isinstance(result, int)
