import logging

from django.core.exceptions import PermissionDenied
from ninja.errors import HttpError
from ninja_extra import NinjaExtraAPI

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
