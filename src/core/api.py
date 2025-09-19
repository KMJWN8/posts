from ninja_extra import NinjaExtraAPI

from src.articles.api import router as articles_router
from src.comments.api import router as comments_router
from src.users.api import router as users_router

from .auth import CustomAuthController

api = NinjaExtraAPI()


api.register_controllers(CustomAuthController)

api.add_router("/users/", users_router)
api.add_router("/articles/", articles_router)
api.add_router("/comments/", comments_router)
