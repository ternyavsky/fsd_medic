from api.models import *
from django.shortcuts import get_object_or_404

#news
def get_news(**kwargs):
    """Получение новостей"""
    return News.objects.filter(**kwargs)


##notes
def get_notes(**kwargs):
    """Получение записей"""
    return Notes.objects.filter(**kwargs)



def get_clinics(**kwargs):
    """Получение списка клиник"""
    return Clinics.objects.filter(**kwargs)


def get_disease(**kwargs):
    """Получение списка болезней"""
    return Disease.objects.filter(**kwargs)


def get_centers(**kwargs):
    """Получение центров"""
    return Centers.objects.filter(**kwargs)


#user
def get_users(**kwargs):
    """Получение пользователей"""
    return User.objects.filter(**kwargs)

def get_groups(**kwargs):
    """Получение групп пользователей"""
    return Groups.objects.filter(**kwargs)

##
