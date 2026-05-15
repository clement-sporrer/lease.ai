import uuid
import datetime
import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch

from app.main import app


def _make_pkg(status: str = "draft") -> MagicMock:
    pkg = MagicMock()
    pkg.id = uuid.uuid4()
    pkg.deal_id = uuid.uuid4()
    pkg.status = status
    pkg.amount_cents = 8_000_000
    pkg.duration_months = 36
    pkg.monthly_payment_cents = 240_000
    pkg.risk_score = 72.0
    pkg.risk_band = "B"
    pkg.sent_at = None
    pkg.created_at = datetime.datetime.now(datetime.timezone.utc)
    pkg.updated_at = datetime.datetime.now(datetime.timezone.utc)
    return pkg


@pytest.mark.anyio
async def test_create_refi_package_returns_201(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="admin")
    pkg = _make_pkg()

    with patch("app.routers.refi.refi_service.create_refi_package", new=AsyncMock(return_value=pkg)):
        with patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                res = await ac.post(
                    f"/deals/{pkg.deal_id}/refi-packages",
                    headers={"Authorization": f"Bearer {token}"},
                )
    assert res.status_code == 201
    assert res.json()["data"]["status"] == "draft"


@pytest.mark.anyio
async def test_financier_decision_approved_returns_200(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="financier")
    pkg = _make_pkg(status="sent")

    deal = MagicMock()
    deal.id = pkg.deal_id
    deal.status = "refi_review"

    dec = MagicMock()
    dec.id = uuid.uuid4()
    dec.refi_package_id = pkg.id
    dec.decision = "approved"
    dec.reason = None
    dec.decided_at = datetime.datetime.now(datetime.timezone.utc)

    with (
        patch("app.routers.refi.refi_service.get_package", new=AsyncMock(return_value=pkg)),
        patch("app.routers.refi.deal_service.get_deal", new=AsyncMock(return_value=deal)),
        patch("app.routers.refi.refi_service.record_decision", new=AsyncMock(return_value=dec)),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post(
                f"/refi-packages/{pkg.id}/decision",
                json={"decision": "approved"},
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 200
    assert res.json()["data"]["decision"] == "approved"


@pytest.mark.anyio
async def test_financier_decision_rejected_without_reason_returns_422(make_token, test_ec_key):
    token = make_token(sub=str(uuid.uuid4()), active_role="financier")
    pkg = _make_pkg(status="sent")

    deal = MagicMock()
    deal.id = pkg.deal_id
    deal.status = "refi_review"

    from app.core.errors import AppError

    with (
        patch("app.routers.refi.refi_service.get_package", new=AsyncMock(return_value=pkg)),
        patch("app.routers.refi.deal_service.get_deal", new=AsyncMock(return_value=deal)),
        patch(
            "app.routers.refi.refi_service.record_decision",
            new=AsyncMock(side_effect=AppError(422, "REASON_REQUIRED", "reason required")),
        ),
        patch("app.core.auth._get_jwks", new=AsyncMock(return_value=test_ec_key["jwks"])),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.post(
                f"/refi-packages/{pkg.id}/decision",
                json={"decision": "rejected"},
                headers={"Authorization": f"Bearer {token}"},
            )
    assert res.status_code == 422
