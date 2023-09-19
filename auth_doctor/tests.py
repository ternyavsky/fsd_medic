from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.urls import reverse
from api.models import Country, Center, Disease
from .models import Doctor
from .services.all_service import get_code_cache_name


class TestClinicReg(APITestCase):
    def setUp(self):
        Country.objects.create(name="Russia")
        Center.objects.create(name="Center_1")
        Disease.objects.create(name="Заболевание 1")
        Disease.objects.create(name="Заболевание 2")

    def test_doctor_create_1(self):
        # все норм
        url = reverse('clinic_create')
        req_data = {
            'name': "test_name",
            'description': "test_description",
            'number': "89856478963",
            'email': "test@yandex.ru",
            'employees_number': 18,
            'supported_diseases': [1, 2],
            'country': 1,
            'city': "Moscow",
            'address': "test address",
            'Center': 1
        }
        response = self.client.post(url, format='json', data=req_data)
        data = response.data
        print(data)
        self.assertEqual(200, response.status_code)
        user_hash = data.get("user_hash")
        url = reverse('create_send_code', kwargs={"user_hash": user_hash})
        response = self.client.get(url)
        print(response.data)
        self.assertEqual(200, response.status_code)
        url = reverse('clinic_verification_code')
        response = self.client.post(url, data={"user_hash": user_hash,
                                               "verification_code": cache.get(get_code_cache_name(user_hash))})
        self.assertEqual(200, response.status_code)
        doctor = Doctor.objects.get(id=1)
        self.assertEqual(req_data["name"], doctor.first_name)
        self.assertEqual(req_data["description"], doctor.middle_name)
        self.assertEqual(req_data["number"], doctor.last_name)
        self.assertEqual(req_data["employees_number"], doctor.phone_number)
        self.assertEqual(req_data["supported_diseases"], doctor.city)
        self.assertEqual(req_data["country"], doctor.country.id)
        self.assertEqual(req_data["city"], doctor.center.id)
        self.assertEqual(req_data["address"], doctor.address)
        self.assertEqual(req_data["Center"], doctor.specialization)


class TestDoctorReg(APITestCase):
    def setUp(self):
        Country.objects.create(name="Russia")
        Center.objects.create(name="Center_1")

    def test_doctor_create_1(self):
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
        self.assertEqual(200, response.status_code)
        user_hash = data.get("user_hash")
        url = reverse('create_send_code', kwargs={"user_hash": user_hash})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        url = reverse('doctor_verification_code')
        response = self.client.post(url, data={"user_hash": user_hash,
                                               "verification_code": cache.get(get_code_cache_name(user_hash))})
        self.assertEqual(200, response.status_code)
        doctor = Doctor.objects.get(id=1)
        self.assertEqual(req_data["first_name"], doctor.first_name)
        self.assertEqual(req_data["middle_name"], doctor.middle_name)
        self.assertEqual(req_data["last_name"], doctor.last_name)
        self.assertEqual(req_data["phone_number"], doctor.phone_number)
        self.assertEqual(req_data["city"], doctor.city)
        self.assertEqual(req_data["country"], doctor.country.id)
        self.assertEqual(req_data["center"], doctor.center.id)
        self.assertEqual(req_data["address"], doctor.address)
        self.assertEqual(req_data["specialization"], doctor.specialization)
        self.assertEqual(req_data["work_experience"], doctor.work_experience)

    def test_doctor_create_2(self):
        # Неправильный код
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
        self.assertEqual(200, response.status_code)
        user_hash = data.get("user_hash")
        url = reverse('create_send_code', kwargs={"user_hash": user_hash})
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        url = reverse('doctor_verification_code')
        response = self.client.post(url, data={"user_hash": user_hash,
                                               "verification_code": "12"})
        self.assertEqual(400, response.status_code)
        self.assertEqual(0, Doctor.objects.all().count())

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
