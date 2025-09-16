from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.schema import TokenRefreshInputSchema, TokenRefreshOutputSchema
from ninja_jwt.tokens import RefreshToken

from .schemas import UserCreateSchema, UserLoginRegisterSchema
from .services import UserCRUD

Auth = JWTAuth

router = Router(tags=["Auth"])


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


@router.post("/token/refresh", response=TokenRefreshOutputSchema)
def refresh_token(request, payload: TokenRefreshInputSchema):
    try:
        refresh = RefreshToken(payload.refresh)
        new_access = str(refresh.access_token)
        return TokenRefreshOutputSchema(access=new_access)
    except Exception:
        raise HttpError(401, "Token is invalid or expired")
