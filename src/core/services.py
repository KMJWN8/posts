# apps/common/crud_base.py

from typing import Any, Dict, Iterable, Type, TypeVar

from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import Http404

M = TypeVar("M", bound=models.Model)


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
            raise Http404(f"{cls.model.__name__} not found")

    @classmethod
    def list(cls) -> Iterable[M]:
        return cls.get_queryset()

    @classmethod
    def retrieve(cls, pk: int) -> M:
        return cls.get_object(pk)

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
        return instance

    @classmethod
    def delete(cls, pk: int, user: Any = None) -> None:
        instance = cls.get_object(pk)
        instance.delete()


def check_ownership(rhs, lhs):
    if rhs != lhs:
        raise PermissionDenied()
