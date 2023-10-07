from django.test import TestCase, Client
from . import models
from db import queries

# Create your tests here.

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory
from unittest.mock import patch

from .views import DoctorsListView
from auth_doctor.models import Doctor
from .serializers import DoctorGetSerializer


