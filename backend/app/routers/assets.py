from typing import Any

from fastapi import APIRouter, Depends

from app._demo_auth import get_current_user_demo
from app.envelope import ok
from app.errors import APIError
from app.state import db, new_id, state_lock

router = APIRouter()


@router.get("/contracts/{contract_id}/assets")
def list_assets(contract_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    items = [a for a in db()["assets"].values() if a["contract_id"] == contract_id]
    return ok(items)


@router.post("/contracts/{contract_id}/assets", status_code=201)
def create_asset(
    contract_id: str, payload: dict[str, Any], user: dict = Depends(get_current_user_demo)
) -> dict:
    if contract_id not in db()["contracts"]:
        raise APIError("ENTITY_NOT_FOUND", "Contract not found", status=404)
    asset_id = new_id("asset")
    asset = {
        "id": asset_id,
        "contract_id": contract_id,
        "name": payload.get("name", "Asset"),
        "category": payload.get("category", "Other"),
        "serial_number": payload.get("serial_number"),
        "quantity": payload.get("quantity", 1),
        "unit_value_cents": payload.get("unit_value_cents", 0),
        "residual_value_cents": payload.get("residual_value_cents", 0),
        "status": "active",
    }
    with state_lock():
        db()["assets"][asset_id] = asset
    return ok(asset)


@router.get("/assets/{asset_id}")
def get_asset(asset_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    a = db()["assets"].get(asset_id)
    if not a:
        raise APIError("ENTITY_NOT_FOUND", "Asset not found", status=404)
    return ok(a)


@router.patch("/assets/{asset_id}")
def patch_asset(
    asset_id: str, payload: dict[str, Any], user: dict = Depends(get_current_user_demo)
) -> dict:
    a = db()["assets"].get(asset_id)
    if not a:
        raise APIError("ENTITY_NOT_FOUND", "Asset not found", status=404)
    editable = {"name", "category", "serial_number", "quantity", "unit_value_cents", "residual_value_cents", "status"}
    with state_lock():
        for k, v in payload.items():
            if k in editable:
                a[k] = v
    return ok(a)
