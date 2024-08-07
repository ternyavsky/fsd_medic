from rest_framework.views import APIView
import jwt
from api.models import Center, Clinic, User
from auth_doctor.models import Doctor
from db.queries import get_centers, get_clinics, get_doctors, get_users
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password


def user_authenticate(number=None, email=None, password=None):
    try:
        user = None
        if number:
            user = get_users(number=number).first()
        elif email:
            user = get_users(email=email).first()
        if check_password(password, user.password):
            return user
        else:
            return None
    except User.DoesNotExist:
        return None


def doctor_authenticate(number=None, password=None):
    try:
        doctors = cache.get_or_set("doctors", get_doctors())
        doctor = doctors.filter(number=number).first()
        if check_password(password, doctor.password):
            return doctor
        else:
            return None
    except Doctor.DoesNotExist:
        return None


def clinic_authenticate(number=None, password=None):
    try:
        clinic = Clinic.objects.filter(number=number).first()
        if check_password(password, clinic.password):
            return clinic
        else:
            return None
    except Clinic.DoesNotExist:
        return None


def center_authenticate(number=None, password=None):
    try:
        centers = cache.get_or_set("centers", get_centers())
        center = centers.filter(number=number).first()
        if password == center.password:
            return center
        else:
            return None
    except Center.DoesNotExist:
        return None
