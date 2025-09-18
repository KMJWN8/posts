from typing import List

from django.contrib.auth.hashers import make_password
from ninja import Router
from ninja.errors import HttpError

from src.core.auth import jwt_auth

from .schemas import UserOutSchema, UserUpdateSchema
from .services import UserCRUD

router = Router(tags=["Users"])


@router.get("/", response=List[UserOutSchema])
def list_users(request):
    return UserCRUD.list()


@router.get("/{user_id}", response=UserOutSchema)
def get_user(request, user_id: int):
    return UserCRUD.retrieve(user_id)


@router.put("/{user_id}", response=UserOutSchema, auth=jwt_auth)
def update_user(request, user_id: int, payload: UserUpdateSchema):
    if request.auth.id != user_id:
        raise HttpError(403, "You can only update your own profile.")

    data = payload.dict(exclude_unset=True)
    if "password" in data:
        data["password"] = make_password(data["password"])
    return UserCRUD.update(request, user_id, data)


@router.delete("/{user_id}", auth=jwt_auth)
def delete_user(request, user_id: int):
    if request.auth.id != user_id:
        raise HttpError(403, "You can only delete your own account.")
    UserCRUD.delete(request, user_id)
    return {"success": True}
