from api.models import *
from django.shortcuts import get_object_or_404
from social.models import *
from fsd_medic.settings import AUTH_USER_MODEL
from api import models

#news
def get_news(**kwargs):
    """Получение новостей"""
    return (News.objects.filter(**kwargs)
        .select_related("center", "disease", "center__country")
        )


def get_likes(**kwargs):
    return (Like.objects.filter(**kwargs)
        .select_related("user", "user__main_center", "user__group", "user__main_center__country",
         "user__country", "news", "news__center", "news__disease", "news__center__country")
        .prefetch_related("user__disease", "user__centers", "user__centers__country")
        )                       
                        
                        
def get_saved(**kwargs):
    return (Saved.objects.filter(**kwargs)
        .select_related("user", "user__main_center", "user__group", "user__main_center__country",
         "user__country", "news", "news__center", "news__disease", "news__center__country")
        .prefetch_related("user__disease", "user__centers", "user__centers__country")
        )


##notes
def get_notes(**kwargs):
    """Получение записей"""
    return (Note.objects.filter(**kwargs)
        .select_related("doctor" , "doctor__group","doctor__country", "doctor__main_center",
         "doctor__main_center__country","user__country","center", "user","user__group", "user__main_center", 
         "user__main_center__country", "doctor__main_center__country","center__country", )
        .prefetch_related("user__disease", "user__centers","user__centers__country",
          "doctor__disease", "doctor__centers", "doctor__centers__country")
        )



def get_clinics(**kwargs):
    """Получение списка клиник"""
    return (Clinic.objects.filter(**kwargs)
        .select_related("country")
        .prefetch_related("supported_diseases")
        )


def get_disease(**kwargs):
    """Получение списка болезней"""
    return Disease.objects.filter(**kwargs)


def get_centers(**kwargs):
    """Получение центров"""
    return (Center.objects.filter(**kwargs)
        .select_related("country")
        )


#user
def get_users(**kwargs):
    """Получение пользователей"""
    return(models.User.objects.filter(**kwargs)
        .select_related("group", "main_center", "country", "main_center__country")
        .prefetch_related("disease", "centers", "centers__country")
        )

def get_groups(**kwargs):
    """Получение групп пользователей"""
    return Group.objects.filter(**kwargs)

##

def get_messages(**kwargs):
    return (Message.objects.filter(**kwargs)
        .select_related("chat", "chat__to_user","chat__to_user__country", "chat__to_user__main_center",
        "chat__to_center","chat__to_user__main_center__country", "chat__from_user","chat__from_user__country",
        "chat__to_user__group",
        "chat__from_user__main_center", "chat__from_user__main_center__country", "chat__from_user__group",
        "chat__from_user__country",
        
        "chat__from_center", "chat__from_center__country", "news", "news__center", "news__disease", "news__center",
        "news__center__country", "user", "user__group", "user__main_center", "user__country",
        "user__main_center__country", "center", "center__country")
        )

def get_chats(**kwargs):
    return Chat.objects.filter(**kwargs)