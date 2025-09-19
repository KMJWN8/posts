import logging
from typing import Any, Dict, Iterable, Type, TypeVar

from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import Http404

M = TypeVar("M", bound=models.Model)

logger = logging.getLogger("src.core.crud")


class BaseCRUD:
    model: Type[M] = None

    @classmethod
    def get_queryset(cls):
        return cls.model.objects.all()

    @classmethod
    def get_object(cls, pk: int) -> M:
        try:
            return cls.get_queryset().get(pk=pk)
        except cls.model.DoesNotExist:
            logger.warning(f"{cls.model.__name__} with ID={pk} not found.")
            raise Http404(f"{cls.model.__name__} not found")

    @classmethod
    def list(cls) -> Iterable[M]:
        logger.info(f"Listing {cls.model.__name__}")
        return cls.get_queryset()

    @classmethod
    def retrieve(cls, pk: int) -> M:
        instance = cls.get_object(pk)
        logger.info(f"Retrieved {cls.model.__name__} ID={pk}")
        return instance

    @classmethod
    def _allowed_fields(cls) -> set:
        # поля модели, которые можно изменять через CRUD (имена полей в модели и *_id для FK)
        names = {
            f.name for f in cls.model._meta.get_fields() if getattr(f, "editable", True)
        }
        # добавить *_id для FK
        for f in cls.model._meta.fields:
            if f.many_to_one or f.one_to_one:
                names.add(f.name + "_id")
        return names

    @classmethod
    def create(cls, data: Dict[str, Any]) -> M:
        # фильтруем лишние поля
        allowed = cls._allowed_fields()
        filtered = {k: v for k, v in data.items() if k in allowed}
        instance = cls.model(**filtered)
        instance.full_clean()
        instance.save()
        logger.info(
            f"Created {cls.model.__name__} ID={instance.pk} by user ID={data.get('author') or 'unknown'}"
        )
        return instance

    @classmethod
    def update(cls, pk: int, data: Dict[str, Any], user: Any = None) -> M:
        instance = cls.get_object(pk)
        allowed = cls._allowed_fields()
        for key, value in data.items():
            if key in allowed:
                setattr(instance, key, value)
        instance.full_clean()
        instance.save()
        user_id = getattr(user, "id", "unknown")
        logger.info(
            f"Updated {cls.model.__name__} ID={pk}. Changed: {data}. By user ID={user_id}"
        )
        return instance

    @classmethod
    def delete(cls, pk: int, user: Any = None) -> None:
        instance = cls.get_object(pk)
        user_id = getattr(user, "id", "unknown")
        logger.warning(f"Deleting {cls.model.__name__} ID={pk} by user ID={user_id}")
        instance.delete()


def check_ownership(rhs, lhs):
    if rhs != lhs:
        raise PermissionDenied()
