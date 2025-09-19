import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import Signal
from django.http import HttpRequest
from ninja_extra import api_controller, http_post
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.schema import TokenObtainPairOutputSchema, TokenRefreshOutputSchema

# Настройка логгера
logger = logging.getLogger("src.users.auth")

jwt_auth = JWTAuth()

# Кастомные сигналы для JWT (опционально, если хотите отделить от стандартных)
jwt_user_login = Signal()
jwt_user_logout = Signal()

User = get_user_model()


@api_controller("/auth/jwt")
class CustomAuthController:
    @http_post(
        "/login",
        response=TokenObtainPairOutputSchema,
    )
    def login(self, request: HttpRequest):
        from ninja_jwt.schema import TokenObtainPairSerializer

        # Получаем данные из запроса
        serializer = TokenObtainPairSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(
                f"Failed login attempt with data: {request.data.get('username')}"
            )
            return {"detail": "Invalid credentials"}, 401

        user = serializer.user
        tokens = serializer.validated_data

        # Отправляем стандартный сигнал Django
        user_logged_in.send(sender=User, request=request, user=user)

        # Отправляем кастомный сигнал (если слушаете где-то ещё)
        jwt_user_login.send(sender=self.__class__, user=user, request=request)

        # Логируем успешный вход
        logger.info(f"User '{user.username}' (ID: {user.id}) logged in via JWT.")

        return tokens

    @http_post("/refresh", response=TokenRefreshOutputSchema)
    def refresh_token(self, request):
        from ninja_jwt.schema import RefreshTokenSerializer

        serializer = RefreshTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return {"detail": "Invalid refresh token"}, 401

        return serializer.validated_data

    @http_post("/verify", auth=None)
    def verify_token(self, request):
        # Токен уже проверен через auth=None + валидация в NinjaJWT
        return {"message": "Token is valid"}

    @http_post("/logout", auth=None)
    def logout(self, request):
        """
        Условный logout. На бэкенде JWT не хранится,
        но мы можем залогировать попытку выхода.
        """
        if hasattr(request, "user") and request.user.is_authenticated:
            user = request.user
            # Отправляем сигнал
            user_logged_out.send(sender=User, request=request, user=user)
            jwt_user_logout.send(sender=self.__class__, user=user, request=request)
            logger.info(f"User '{user.username}' (ID: {user.id}) logged out.")
        else:
            logger.info("Anonymous user attempted logout.")

        return {"success": True}
