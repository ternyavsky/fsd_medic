from django.contrib.auth import get_user_model

from api import models
from api.models import *
from auth_doctor.models import Doctor
from social.models import *

User = get_user_model()


# news
def get_news(**kwargs):
    """Получение новостей"""
    return (
        News.objects.select_related(
            "clinic",
            "disease",
        )
        .prefetch_related("news_images", "news_videos")
        .filter(**kwargs)
    )


def get_likes(**kwargs):
    return (
        Like.objects.filter(**kwargs)
        .select_related(
            "user",
            "user__group",
            "news",
            "news__center",
            "news__disease",
        )
        .prefetch_related(
            "user__disease",
            "user__centers",
        )
    )


def get_subscribes(**kwargs):
    return Subscribe.objects.filter(**kwargs).select_related(
        "clinic", "user", "main_doctor"
    )


def get_cities(**kwargs):
    return City.objects.filter(**kwargs)


def get_countries(**kwargs):
    return Country.objects.filter(**kwargs)


def get_saved(**kwargs):
    return (
        Saved.objects.filter(**kwargs)
        .select_related(
            "user",
            "user__group",
            "news",
            "news__center",
            "news__disease",
        )
        .prefetch_related(
            "user__disease",
            "user__centers",
        )
    )


# notes
def get_notes(**kwargs):
    """Получение записей"""
    return (
        Note.objects.select_related(
            "user", "center", "clinic", "center__admin", "clinic__admin"
        )
        .prefetch_related(
            "center__employees",
            "user__centers",
            "center__supported_diseases",
            "user__disease",
            "clinic__supported_diseases",
            "doctors"
        )
        .filter(**kwargs)
    )


def get_clinics(**kwargs):
    """Получение списка клиник"""
    return (
        Clinic.objects.select_related(
            "center",
        )
        .prefetch_related(
            "supported_diseases",
            "center__supported_diseases",
        )
        .filter(**kwargs)
    )


def get_disease(**kwargs):
    """Получение списка болезней"""

    return Disease.objects.filter(**kwargs)


def get_centers(**kwargs):
    """Получение центров"""
    return (
        Center.objects.select_related("admin")
        .prefetch_related(
            "supported_diseases",
            "employees",
            "admin__centers",
            "admin__disease",
        )
        .filter(**kwargs)
    )


# user
def get_users(**kwargs):
    """Получение пользователей"""
    return (
        User.objects.filter(**kwargs)
        .select_related("clinic", "country", "city")
        .prefetch_related(
            "disease",
            "centers",
            "centers__employees",
            "centers__supported_diseases",
            "clinic__supported_diseases",
        )
    )


def get_doctors(**kwargs):
    return (
        Doctor.objects.filter(**kwargs)
        .select_related(
            "center",
            "clinic",
        )
        .prefetch_related("center__employees", "center__supported_diseases")
    )


def get_access(**kwargs):
    """Получение доступа"""
    return (
        Access.objects.filter(**kwargs)
        .select_related("user")
        .prefetch_related(
            "access_accept",
            "access_unaccept",
            "access_accept__centers",
            "access_unaccept__centers",
            "access_accept__disease",
            "access_unaccept__disease",
            "user__disease",
        )
    )


def get_groups(**kwargs):
    """Получение групп пользователей"""
    return Group.objects.filter(**kwargs)


def get_notifications(**kwargs):
    return (
        Notification.objects.filter(**kwargs)
        .select_related("user", "user__clinic", "user__country", "user__city")
        .prefetch_related("user__disease", "user__centers")
    )


##


def get_messages(**kwargs):
    return (
        Message.objects.select_related(
            "chat",
            "news",
            "note",
            "user",
            "doctor",
        )
        .prefetch_related("user__disease", "chat__users", "chat__doctors")
        .filter(**kwargs)
    )


def get_chats(**kwargs):
    return Chat.objects.prefetch_related(
        "users__centers", "users__disease", "doctors"
    ).filter(**kwargs)
