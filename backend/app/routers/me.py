from fastapi import APIRouter, Depends
from app.core.auth import get_current_user

router = APIRouter()


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)) -> dict:
    return {
        "user_id": current_user["user_id"],
        "active_role": current_user["active_role"],
    }
