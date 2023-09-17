from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.urls import reverse
from api.models import Country, Center

from .services.all_service import get_code_cache_name


class TestEmailLogin(APITestCase):
    def setUp(self):
        Country.objects.create(name="Russia")
        Center.objects.create(name="Center_1")

    def test_doctor_valid_1(self):
        # все норм
        url = reverse('doctor_create')
        req_data = {
            "first_name": "qwer",
            'middle_name': "qwer",
            "last_name": "qwer",
            "phone_number": "89743251489",
            "city": "Moscow",
            "country": 1,
            "center": 1,
            "address": "qwer",
            "specialization": "sadasdas",
            "work_experience": 3.5
        }
        response = self.client.post(url, format='json', data=req_data)
        data = response.data
        print(data)
        self.assertEqual(200, response.status_code)
        user_hash = data.get("user_hash")
        url = reverse('doctor_create_send_code', kwargs={"user_hash": user_hash})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_doctor_valid_2(self):
        # невалидный телефон
        url = reverse('doctor_create')
        req_data = {
            "first_name": "qwer",
            'middle_name': "qwer",
            "last_name": "qwer",
            "phone_number": "546841",
            "city": "Moscow",
            "country": 1,
            "center": 1,
            "address": "qwer",
            "specialization": "sadasdas",
            "work_experience": 3.5
        }
        response = self.client.post(url, format='json', data=req_data)
        data = response.data
        self.assertEqual(400, response.status_code)
        self.assertEqual(True, "phone_number" in data)

    def test_doctor_valid_3(self):
        # нет страны и центра
        url = reverse('doctor_create')
        req_data = {
            "first_name": "qwer",
            'middle_name': "qwer",
            "last_name": "qwer",
            "phone_number": "546841",
            "city": "Moscow",
            "country": 2,
            "center": 2,
            "address": "qwer",
            "specialization": "sadasdas",
            "work_experience": 3.5
        }
        response = self.client.post(url, format='json', data=req_data)
        data = response.data
        self.assertEqual(400, response.status_code)
        self.assertEqual(True, "country" in data)
        self.assertEqual(True, "center" in data)

    def test_doctor_valid_4(self):
        # Много цифр в опыте
        url = reverse('doctor_create')
        req_data = {
            "first_name": "qwer",
            'middle_name': "qwer",
            "last_name": "qwer",
            "phone_number": "546841",
            "city": "Moscow",
            "country": 1,
            "center": 1,
            "address": "qwer",
            "specialization": "sadasdas",
            "work_experience": 3.5344
        }
        response = self.client.post(url, format='json', data=req_data)
        data = response.data
        self.assertEqual(400, response.status_code)
        self.assertEqual(True, "work_experience" in data)
