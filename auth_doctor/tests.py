from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient

from api.models import Country, Disease, City
from .models import LinkToInterview
from .serializers import ClinicCreateSerializer
from .views import ClinicDataPast


class ClinicDataPastTestCase(TestCase):
    def setUp(self):
        Disease.objects.create(name="Заболевание 1")
        Country.objects.create(name="Россия")
        City.objects.create(name="Москва")
        self.client = Client()
        self.factory = APIRequestFactory()
        self.clinic_data = {
            "name": "Test Clinics",
            "address": "123 Main Stre",
            "number": "+79314341234",
            "description": "lorem lorem",
            "email": "test@example.com",
            "country": "Россия",
            #"center": 1,
            "city": "Москва",
            "supported_diseases": [1],

        }

    def test_post_clinic_data_past(self):
        serializer = ClinicCreateSerializer(data=self.clinic_data)
        if not serializer.is_valid():
            print(serializer.errors, "errors")
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
        self.assertEqual(obj["number"], self.clinic_data["number"])


class ClinicInterviewCreateTestCase(TestCase):
    def setUp(self):
        Disease.objects.create(name="Name")
        Country.objects.create(name="Россия")
        City.objects.create(name="Москва")
        self.clinic_data = {
            "name": "Test Clinic",
            "address": "123 Main St",
            "number": "+79314341234",
            "email": "test@example.com",
            "country": "Россия",
            "city": "Москва",
            "supported_diseases": [1]
        }
        self.client = APIClient()
        self.clinic_hash = "1234567890"
        cache.set(self.clinic_hash, self.clinic_data)
        self.datetime = "2022-01-01T12:00:00Z"
        self.data = {"datetime": self.datetime}
        self.link = LinkToInterview.objects.create(link=self.clinic_hash)


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
        self.assertEqual(response.data["message"],
                         "Такой сессии входа нет или время входы вышло, зарегистрируйтесь заново")
        self.link.refresh_from_db()
