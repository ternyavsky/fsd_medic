from django.contrib.auth import get_user_model

from api import models
from api.models import *
from auth_doctor.models import Doctor
from social.models import *
User = get_user_model()

# news
def get_news(**kwargs):
    """Получение новостей"""
    return (News.objects
            .select_related("center", "disease", "center__country")
            .prefetch_related("center__employees", "center__supported_diseases")
            .filter(**kwargs)
            )


def get_likes(**kwargs):
    return (Like.objects.filter(**kwargs)
            .select_related("user", "user__main_center", "user__group", "user__main_center__country",
                            "user__country", "news", "news__center", "news__disease", "news__center__country")
            .prefetch_related("user__disease", "user__centers", "user__centers__country")
            )


def get_cities(**kwargs):
    return City.objects.filter(**kwargs)


def get_countries(**kwargs):
    return Country.objects.filter(**kwargs).prefetch_related("cities")


def get_saved(**kwargs):
    return (Saved.objects.filter(**kwargs)
            .select_related("user", "user__main_center", "user__group", "user__main_center__country",
                            "user__country", "news", "news__center", "news__disease", "news__center__country")
            .prefetch_related("user__disease", "user__centers", "user__centers__country")
            )


# notes
def get_notes(**kwargs):
    """Получение записей"""
    return (Note.objects
            .select_related("doctor", "user", "center", "user__group", "user__main_center", "clinic",
                            "user__country", "doctor__country", "doctor__center", "center__admin", "center__country",
                            "clinic__admin")
            .prefetch_related("center__employees", "user__centers", "center__supported_diseases", "user__disease",
                              "clinic__supported_diseases")
            .filter(**kwargs)
            )


def get_clinics(**kwargs):
    """Получение списка клиник"""
    return (Clinic.objects
            .select_related("country", "center", "center__country", "city")
            .prefetch_related("employees", "supported_diseases", "center__supported_diseases",
                              "center__employees", "country__cities")
            .filter(**kwargs)
            )


def get_disease(**kwargs):
    """Получение списка болезней"""
    return Disease.objects.filter(**kwargs)


def get_centers(**kwargs):
    """Получение центров"""
    return (Center.objects.filter(**kwargs)
            .select_related("country", "admin", "city")
            .prefetch_related("supported_diseases", "employees", "admin__centers", "admin__disease",
                              "country__cities"
                              )

            )


# user
def get_users(**kwargs):
    """Получение пользователей"""
    return (User.objects.filter(**kwargs)
            .select_related("group", "main_center", "country", "city", "interest")
            .prefetch_related("centers", "disease", "main_center__employees", "centers__employees",
                              "main_center__supported_diseases",
                              "centers__supported_diseases", "country__cities")
            )


def get_doctors(**kwargs):
    return (Doctor.objects.filter(**kwargs)
            .select_related("country", "center", "clinic")
            )


def get_access(**kwargs):
    """Получение доступа"""
    return (Access.objects.filter(**kwargs)
            .select_related("user")
            .prefetch_related("access_accept", "access_unaccept")
            )


def get_groups(**kwargs):
    """Получение групп пользователей"""
    return Group.objects.filter(**kwargs)


##


def get_messages(**kwargs):
    return (Message.objects.
            select_related("chat", "news", "note", "user", "center", "doctor", )
            .prefetch_related("user__centers", "user__disease", "chat__users", "chat__centers", "chat__doctors")
            .filter(**kwargs)
            )


def get_chats(**kwargs):
    return (Chat.objects.
            prefetch_related("users", "centers", "doctors")
            .filter(**kwargs))
