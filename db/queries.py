from api.models import *
from django.shortcuts import get_object_or_404

#news
def get_news(**kwargs):
    """Получение новостей"""
    return News.objects.filter(**kwargs)


def get_likes(**kwargs):
    return Like.objects.filter(**kwargs)


def get_saved(**kwargs):
    return Saved.objects.filter(**kwargs)


##notes
def get_notes(**kwargs):
    """Получение записей"""
    return Note.objects.filter(**kwargs)



def get_clinics(**kwargs):
    """Получение списка клиник"""
    return Clinic.objects.filter(**kwargs)


def get_disease(**kwargs):
    """Получение списка болезней"""
    return Disease.objects.filter(**kwargs)


def get_centers(**kwargs):
    """Получение центров"""
    return Center.objects.filter(**kwargs)


#user
def get_users(**kwargs):
    """Получение пользователей"""
    return User.objects.filter(**kwargs)

def get_groups(**kwargs):
    """Получение групп пользователей"""
    return Group.objects.filter(**kwargs)

##
