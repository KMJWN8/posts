from ninja_extra import NinjaExtraAPI

from src.articles.api import router as articles_router
from src.comments.api import router as comments_router
from src.core.exceptions import configure_exception_handlers
from src.users.api import router as users_router

from .auth import CustomAuthController

api = NinjaExtraAPI()

configure_exception_handlers(api)

api.register_controllers(CustomAuthController)

api.add_router("/users/", users_router)
api.add_router("/articles/", articles_router)
api.add_router("/comments/", comments_router)
