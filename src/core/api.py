from ninja import NinjaAPI

from src.articles.api import router as articles_router
from src.comments.api import router as comments_router
from src.users.api import router as users_router

api = NinjaAPI()

api.add_router("/users/", users_router)
api.add_router("/articles/", articles_router)
api.add_router("/comments/", comments_router)
