from typing import List

from django.contrib.auth.hashers import make_password
from ninja import Router
from ninja_extra import permissions

from src.core.auth import jwt_auth
from src.core.services import check_ownership

from .schemas import UserOutSchema, UserUpdateSchema
from .services import UserCRUD

router = Router(tags=["Users"])


@router.get(
    "/",
    response=List[UserOutSchema],
    permissions=[permissions.IsAdminUser],
    auth=jwt_auth,
)
def list_users(request):
    return UserCRUD.list()


@router.get(
    "/{user_id}",
    response=UserOutSchema,
    permissions=[permissions.IsAuthenticated],
    auth=jwt_auth,
)
def get_user(request, user_id: int):
    return UserCRUD.retrieve(user_id)


@router.put(
    "/{user_id}",
    response=UserOutSchema,
    permissions=[permissions.IsAuthenticated],
    auth=jwt_auth,
)
def update_user(request, user_id: int, payload: UserUpdateSchema):
    check_ownership(request.auth.id, user_id)
    data = payload.dict(exclude_unset=True)
    if "password" in data:
        data["password"] = make_password(data["password"])
    return UserCRUD.update(user_id, data)


@router.delete("/{user_id}", permissions=[permissions.IsAuthenticated], auth=jwt_auth)
def delete_user(request, user_id: int):
    check_ownership(request.auth.id, user_id)
    UserCRUD.delete(user_id)
    return {"success": True}
