from api.models import *
from django.shortcuts import get_object_or_404

def news_filter(**kwargs):
    """Фильтр  для News в блоке get_queryset"""
    return News.objects.filter(**kwargs)

def get_news():
    """Получение новостей"""
    return News.objects.all()
def get_news_by_args(**kwargs):
    """Получение новостей по аргументам"""
    return News.objects.get(**kwargs)


def get_centers():
    """Получение центров"""
    return Centers.objects.all()

def get_notes():
    """Получение списка записей"""
    return Notes.objects.all()

def get_note(**kwargs):
    """Получение записи по аргументам"""
    return Notes.objects.get(**kwargs)



def get_clinics():
    """Получение списка клиник"""
    return Clinics.objects.all()
def get_disease():
    """Получение списка болезней"""
    return Disease.objects.all()

def get_users():
    """Получение списка пользователей"""
    return User.objects.all()