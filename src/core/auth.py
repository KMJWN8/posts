import logging

from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.http import HttpRequest
from ninja.errors import HttpError
from ninja_extra import api_controller, http_post
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.exceptions import TokenError
from ninja_jwt.schema import (
    TokenObtainPairInputSchema,
    TokenObtainPairOutputSchema,
    TokenRefreshInputSchema,
    TokenRefreshOutputSchema,
)
from ninja_jwt.tokens import RefreshToken

from src.users.schemas import UserCreateSchema

from .schemas import RegisterSuccessSchema

logger = logging.getLogger("src.core.auth")

jwt_auth = JWTAuth()
User = get_user_model()


@api_controller("/auth", tags=["Auth"])
class CustomAuthController:
    @http_post("/login", response=TokenObtainPairOutputSchema, auth=None)
    def login(self, request: HttpRequest, data: TokenObtainPairInputSchema):
        user = authenticate(username=data.username, password=data.password)
        if not user:
            raise HttpError(401, "Invalid credentials")

        refresh = RefreshToken.for_user(user)

        user_logged_in.send(sender=User, request=request, user=user)
        logger.info(f"User '{user.username}' (ID: {user.id}) logged.")

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "username": data.username,
        }

    @http_post(
        "/register",
        response={200: RegisterSuccessSchema, 201: RegisterSuccessSchema},
        auth=None,
    )
    def register(self, request: HttpRequest, data: UserCreateSchema):
        if User.objects.filter(username=data.username).exists():
            raise HttpError(400, "Username already exists")

        try:
            user = User.objects.create_user(
                username=data.username, password=data.password
            )

            logger.info(f"New user '{user.username}' registered and logged in")
            return 201, {"success": True, "message": "User registered successfully"}

        except Exception as e:
            logger.error(f"Registration failed for {data.username}: {str(e)}")
            raise HttpError(500, "Registration failed")

    @http_post(
        "/refresh",
        response=TokenRefreshOutputSchema,
        auth=None,
    )
    def refresh_token(self, request, data: TokenRefreshInputSchema):
        try:
            refresh_token = RefreshToken(data.refresh)
            access_token = str(refresh_token.access_token)

            return {
                "refresh": str(refresh_token),
                "access": access_token,
            }
        except TokenError:
            raise HttpError(401, "Invalid refresh token")

    @http_post("/logout", auth=jwt_auth)
    def logout(self, request):
        user = request.user
        user_logged_out.send(sender=User, request=request, user=user)
        logger.info(f"User '{user.username}' (ID: {user.id}) logged out.")
        return {"success": True}
