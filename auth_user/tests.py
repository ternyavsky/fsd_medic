# Create your tests here.
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from rest_framework import status
from api.models import *
from api.serializers import AccessSerializer

class VerifyCodeServiceTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.group = Group.objects.create(name="Пользователи")
        self.news = News.objects.create(title="Test title")
        self.city = City.objects.create(name="Москва")
        self.country = Country.objects.create(name="Россия")
        self.user = User.objects.create(
            number="+79991119911", 
            password="test",
            group=self.group,
            country=self.country,
            verification_code=1234,
            city=self.city)

    def test_verify_code_service_valid_code(self):
        url = reverse('verify-code') # Assuming there is a URL named 'verify-code' defined in urls.py
        data = {'number': self.user.number, 'verification_code': 1234}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'User verified successfully')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_required)

    def test_verify_code_service_invalid_code(self):
        url = reverse('verify-code') # Assuming there is a URL named 'verify-code' defined in urls.py
        data = {'number': '123456789', 'verification_code': 1234}
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['error'], 'User does not exist')
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_required)

    def test_verify_code_service_user_not_found(self):
        url = reverse('verify-code') # Assuming there is a URL named 'verify-code' defined in urls.py
        data = {'number': self.user.number, 'verification_code': 4321}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid verification code')

