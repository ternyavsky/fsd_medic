# Create your tests here.
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status

from api.models import *
from api.serializers import AccessSerializer
