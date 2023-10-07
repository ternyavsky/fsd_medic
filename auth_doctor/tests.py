from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.urls import reverse
from api.models import Country, Center, Disease, Clinic, City
from .models import Doctor
from .services.all_service import get_code_cache_name

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient
from unittest.mock import patch

from .views import ClinicDataPast
from .models import LinkToInterview
from .serializers import ClinicCreateSerializer, DoctorDataResponseSerializer


class ClinicDataPastTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = APIRequestFactory()
        self.clinic_data = {
            "name": "Test Clinic",
            "address": "123 Main St",
            "number": "555-555-5555",
            "email": "test@example.com",
            "country": "Russia",
            "city": "Moscow",
        }


    def test_post_clinic_data_past(self):
        serializer = ClinicCreateSerializer(data=self.clinic_data)
        if not serializer.is_valid():
            print(serializer.errors)
        self.assertTrue(serializer.is_valid())
        request = self.factory.post(reverse('clinic_create'), data=self.clinic_data)
        response = ClinicDataPast.as_view()(request)
        obj = cache.get(response.data["clinic_hash"])
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"],
                         f"Код для регистрации клиники отправлен на номер {self.clinic_data['number']}")
        self.assertTrue(LinkToInterview.objects.filter(link=response.data["clinic_hash"]).exists())
        self.assertEqual(LinkToInterview.objects.get(link=response.data["clinic_hash"]).used, False)
        self.assertEqual(LinkToInterview.objects.get(link=response.data["clinic_hash"]).link,
                         response.data["clinic_hash"])
        self.assertEqual(obj["name"], self.clinic_data["name"])
        self.assertEqual(obj["address"], self.clinic_data["address"])
        self.assertEqual(obj["email"], self.clinic_data["email"])
        self.assertEqual(obj["city"], self.clinic_data["city"])
        self.assertEqual(obj["country"], self.clinic_data["country"])
        self.assertEqual(obj["number"], self.clinic_data["number"])


class ClinicInterviewCreateTestCase(TestCase):
    def setUp(self):
        Disease.objects.create(name="Name")
        Country.objects.create(name="Russia")
        City.objects.create(name="Moscow")
        self.clinic_data = {
            "name": "Test Clinic",
            "address": "123 Main St",
            "number": "555-555-5555",
            "email": "test@example.com",
            "country": "Russia",
            "city": "Moscow",
            "supported_diseases": [1]
        }
        self.client = APIClient()
        self.clinic_hash = "1234567890"
        cache.set(self.clinic_hash, self.clinic_data)
        self.datetime = "2022-01-01T12:00:00Z"
        self.data = {"datetime": self.datetime}
        self.link = LinkToInterview.objects.create(link=self.clinic_hash)

    def test_post_success(self):
        url = reverse("clinic_interview", args=[self.clinic_hash])
        response = self.client.post(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Успешно создан")
        self.link.refresh_from_db()
        self.assertTrue(self.link.used)

    def test_post_failure_already_used(self):
        self.link.used = True
        self.link.save()
        url = reverse("clinic_interview", args=[self.clinic_hash])
        response = self.client.post(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["error"], "Ссылка уже использовалась")
        self.link.refresh_from_db()
        self.assertTrue(self.link.used)

    def test_post_failure_cache_miss(self):
        cache.delete(self.clinic_hash)
        url = reverse("clinic_interview", args=[self.clinic_hash])
        response = self.client.post(url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["message"], "Такой сессии входа нет или время входы вышло, зарегистрируйтесь заново")
        self.link.refresh_from_db()
