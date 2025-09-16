from ninja import NinjaAPI
from ninja_jwt.routers.obtain import obtain_pair_router

from src.articles.api import router as articles_router
from src.comments.api import router as comments_router
from src.users.api import router as users_router
from src.users.auth import router as auth_router

api = NinjaAPI()

api.add_router("/auth/", auth_router)
api.add_router("/users/", users_router)
api.add_router("/articles/", articles_router)
api.add_router("/comments/", comments_router)
