from rest_framework.views import APIView
import jwt
from api.models import Center, Clinic
from auth_doctor.models import Doctor
from db.queries import get_centers, get_clinics, get_doctors
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password


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
        clinics = cache.get_or_set("clinics", get_clinics())
        clinic = clinics.filter(number=number).first()
        if password == clinic.password:
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
    
