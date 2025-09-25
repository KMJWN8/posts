import logging
from typing import Any, Dict, Iterable, Type, TypeVar

from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import Http404

M = TypeVar("M", bound=models.Model)

logger = logging.getLogger("src.core.services")


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
        names = {
            f.name for f in cls.model._meta.get_fields() if getattr(f, "editable", True)
        }

        for f in cls.model._meta.fields:
            if f.many_to_one or f.one_to_one:
                names.add(f.name + "_id")
        return names

    @classmethod
    def _mask_sensitive_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        masked = {}
        for k, v in data.items():
            if k.lower() == "password":
                masked[k] = "[REDACTED]"
            else:
                masked[k] = v
        return masked

    @classmethod
    def create(cls, data: Dict[str, Any]) -> M:
        allowed = cls._allowed_fields()
        filtered = {k: v for k, v in data.items() if k in allowed}
        instance = cls.model(**filtered)
        instance.full_clean()
        instance.save()
        logger.info(
            f"Created {cls.model.__name__} ID={instance.pk} by user ID={data.get('author_id')}"
        )
        return instance

    @classmethod
    def update(cls, pk: int, data: Dict[str, Any], user_id: int = None) -> M:
        instance = cls.get_object(pk)
        allowed = cls._allowed_fields()
        for key, value in data.items():
            if key in allowed:
                setattr(instance, key, value)
        instance.full_clean()
        instance.save()
        safe_data = cls._mask_sensitive_data(data)
        logger.info(
            f"Updated {cls.model.__name__} ID={pk}. Changed: {safe_data}. By user ID={user_id or pk}"
        )
        return instance

    @classmethod
    def delete(cls, pk: int, user_id: int = None) -> None:
        instance = cls.get_object(pk)
        logger.warning(
            f"Deleting {cls.model.__name__} ID={pk} by user ID={user_id or pk}"
        )
        instance.delete()


def check_ownership(rhs, lhs):
    if rhs != lhs:
        raise PermissionDenied()
