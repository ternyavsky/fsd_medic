from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient

from api.models import Country, Disease, City
from .models import LinkToInterview
from .serializers import ClinicCreateSerializer
from .views import ClinicDataPast
