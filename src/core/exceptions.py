import logging

from django.core.exceptions import PermissionDenied
from django.http import Http404
from ninja.errors import HttpError
from ninja_extra import NinjaExtraAPI
from ninja_jwt.exceptions import InvalidToken, TokenError

logger = logging.getLogger("src.core.api")


def configure_exception_handlers(api: NinjaExtraAPI):

    @api.exception_handler(PermissionDenied)
    def permission_denied_handler(request, exc):
        logger.warning(
            f"Access denied: {request.path} - User: {getattr(request.user, 'username', 'Anonymous')}"
        )
        return api.create_response(request, {"detail": "Permission denied"}, status=403)

    @api.exception_handler(HttpError)
    def http_error_handler(request, exc: HttpError):
        if exc.status_code == 401:
            logger.info(
                f"Unauthorized access attempt to {request.path} - User: {getattr(request.user, 'username', 'Anonymous')}"
            )
        else:
            logger.warning(f"HTTP {exc.status_code} at {request.path}: {exc.message}")
        return api.create_response(
            request, {"detail": exc.message}, status=exc.status_code
        )

    @api.exception_handler(InvalidToken)
    def invalid_token_handler(request, exc):
        logger.warning(f"Invalid token attempt: {request.path}")
        return api.create_response(
            request,
            {"detail": "Invalid or expired token", "code": "token_invalid"},
            status=401,
        )

    @api.exception_handler(TokenError)
    def token_error_handler(request, exc):
        logger.warning(f"Token error: {str(exc)} - Path: {request.path}")
        return api.create_response(
            request,
            {
                "detail": "Token error occurred",
                "code": "token_error",
                "message": str(exc),
            },
            status=401,
        )

    @api.exception_handler(Http404)
    def not_found_handler(request, exc):
        logger.info(f"404 Not Found: {request.path}")
        return api.create_response(
            request, {"detail": "Resource not found"}, status=404
        )

    @api.exception_handler(Exception)
    def general_exception_handler(request, exc):
        logger.error(f"Unexpected error in {request.path}: {str(exc)}", exc_info=True)
        return api.create_response(
            request,
            {"detail": "Internal server error", "code": "internal_error"},
            status=500,
        )
