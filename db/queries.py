from api.models import *
from django.shortcuts import get_object_or_404

#news
def get_news(**kwargs):
    """Получение новостей"""
    if kwargs:
        return News.objects.filter(**kwargs)
    else:
        return News.objects.all()
##

##notes
def get_notes(**kwargs):
    """Получение записей"""
    if kwargs:
        return Notes.objects.filter(**kwargs)
    else:
        return Notes.objects.all()
##

def get_clinics():
    """Получение списка клиник"""
    return Clinics.objects.all()
def get_disease():
    """Получение списка болезней"""
    return Disease.objects.all()
def get_centers():
    """Получение центров"""
    return Centers.objects.all()

#user
def get_users(**kwargs):
    """Получение пользователей"""
    if kwargs:
        return User.objects.filter(**kwargs)
    else:

        return User.objects.all()

##