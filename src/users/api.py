from django.contrib.auth import get_user_model
from ninja import Router
from ninja_jwt.tokens import RefreshToken

from .schemas import UserCreateSchema, UserOutSchema, UserRegisterResponseSchema

User = get_user_model()
router = Router(tags=["Auth"])


@router.post("/register", response=UserRegisterResponseSchema)
def register(request, payload: UserCreateSchema):
    user = User.objects.create_user(
        username=payload.username, password=payload.password, bio=payload.bio or ""
    )
    refresh = RefreshToken.for_user(user)
    return {
        "user": user,
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
