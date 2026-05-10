from fastapi import APIRouter, Depends

from app.core.auth import get_current_user
from app.core.roles import UserRole
from app.schemas.auth import ActiveRoleRequest, ActiveRoleResponse, MeResponse
from app.services import auth_service

router = APIRouter()


@router.get("/me", response_model=MeResponse)
async def me(current_user: dict = Depends(get_current_user)) -> MeResponse:
    role = current_user["active_role"]
    return MeResponse(
        user_id=current_user["user_id"],
        active_role=role.value if isinstance(role, UserRole) else role,
    )


@router.post("/me/active-role", response_model=ActiveRoleResponse)
async def update_active_role(
    body: ActiveRoleRequest,
    current_user: dict = Depends(get_current_user),
) -> ActiveRoleResponse:
    result = await auth_service.set_active_role(current_user["user_id"], body.role)
    return ActiveRoleResponse(**result)
