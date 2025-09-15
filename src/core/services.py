# apps/common/crud_base.py

from typing import Type

from django.db import models
from django.http import Http404
from pydantic import BaseModel


class BaseCRUD:
    model: Type[models.Model] = None
    create_schema: Type[BaseModel] = None
    update_schema: Type[BaseModel] = None
    out_schema: Type[BaseModel] = None

    @classmethod
    def get_queryset(cls):
        return cls.model.objects.all()

    @classmethod
    def get_object(cls, pk: int):
        try:
            return cls.get_queryset().get(pk=pk)
        except cls.model.DoesNotExist:
            raise Http404(f"{cls.model.__name__} not found")

    @classmethod
    def list(cls):
        return cls.get_queryset()

    @classmethod
    def retrieve(cls, pk: int):
        return cls.get_object(pk)

    @classmethod
    def create(cls, data: dict):
        instance = cls.model(**data)
        instance.full_clean()
        instance.save()
        return instance

    @classmethod
    def update(cls, pk: int, data: dict):
        instance = cls.get_object(pk)
        for key, value in data.items():
            setattr(instance, key, value)
        instance.full_clean()
        instance.save()
        return instance

    @classmethod
    def delete(cls, pk: int):
        instance = cls.get_object(pk)
        instance.delete()
