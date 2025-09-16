from src.core.services import BaseCRUD

from .models import User
from .schemas import UserCreateSchema, UserOutSchema, UserUpdateSchema


class UserCRUD(BaseCRUD):
    model = User
    create_schema = UserCreateSchema
    update_schema = UserUpdateSchema
    out_schema = UserOutSchema
