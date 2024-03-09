from django.db import models
from typing import TYPE_CHECKING, Any, Generic, NamedTuple, TypeVar, overload
from django.db.models import Count, QuerySet

if TYPE_CHECKING:
    from api.models import User
from django.db.models.base import Model
import abc


class SimpleQuerySet(models.QuerySet):
    def filter_by_user(self, user: "User"):
        self.filter(user=user)


class SimpleManager(models.Manager):
    def get_queryset(self):
        return SimpleQuerySet(self.model)


class AbstractManagerMeta(abc.ABCMeta, type(models.Manager)):
    pass


class AbstractQuerySetMeta(abc.ABCMeta, type(models.QuerySet)):
    pass


class BaseQuerySet(models.QuerySet, metaclass=AbstractQuerySetMeta):
    @abc.abstractmethod
    def filter_by_user(self, user: "User"):
        self.filter(user=user)


class BaseManager(models.Manager, metaclass=AbstractManagerMeta):
    @abc.abstractmethod
    def get_queryset(self):
        pass
