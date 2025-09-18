from typing import List

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.schema import TokenRefreshInputSchema, TokenRefreshOutputSchema
from ninja_jwt.tokens import RefreshToken

from src.core.auth import jwt_auth

from .schemas import (
    UserCreateSchema,
    UserLoginRegisterSchema,
    UserOutSchema,
    UserUpdateSchema,
)
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


@router.post("/register", response=UserLoginRegisterSchema)
def register_user(request, payload: UserCreateSchema):
    data = payload.dict()
    data["password"] = make_password(data["password"])

    user = UserCRUD.create(data)

    refresh = RefreshToken.for_user(user)
    access = str(refresh.access_token)

    return {
        "user": user,
        "access": access,
        "refresh": str(refresh),
    }


@router.post("/login", response=UserLoginRegisterSchema)
def login_user(request, username: str, password: str):
    user = authenticate(username=username, password=password)
    if not user:
        raise HttpError(401, "Invalid username or password")

    refresh = RefreshToken.for_user(user)
    return {"user": user, "access": str(refresh.access_token), "refresh": str(refresh)}


@router.post("/token-refresh", response=TokenRefreshOutputSchema)
def refresh_token(request, payload: TokenRefreshInputSchema):
    try:
        refresh = RefreshToken(payload.refresh)
        new_access = str(refresh.access_token)
        return TokenRefreshOutputSchema(access=new_access)
    except Exception:
        raise HttpError(401, "Token is invalid or expired")
