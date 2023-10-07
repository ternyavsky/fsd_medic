from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from api.models import Country, Center, Disease, User, Group, News
from social.models import Chat


class TestChatCreate(APITestCase):
    def setUp(self):
        self.group = Group.objects.create(name="qewwq")
        self.user = User.objects.create(number="123", group=self.group)
        self.user1 = User.objects.create(number="1234", group=self.group)
        Country.objects.create(name="Russia")
        self.center1 = Center.objects.create(name="Center_1")
        Disease.objects.create(name="Disease_1")
        Disease.objects.create(name="Disease_2")
        News.objects.create(title="ssa", text="ssdda", center=self.center1)

    def test_clinic_create_1(self):
        # все норм

        url = reverse('chat_create')

        req_data = {
            'user_ids': [1, 2],
            'center_ids': [1],
        }
        response = self.client.post(url, format='json', data=req_data)
        data = response.data
        print(data)
        self.assertEqual(200, response.status_code)
        chat = Chat.objects.get(id=1)
        self.assertEqual(chat.users.all()[0].id, req_data["user_ids"][0])
        self.assertEqual(chat.users.all()[1].id, req_data["user_ids"][1])
        self.assertEqual(chat.centers.all()[0].id, req_data["center_ids"][0])

    def test_clinic_create_2(self):
        # все норм

        url = reverse('chat_create')

        req_data = {
            'user_ids': [1, 2],
            'center_ids': [],
        }
        response = self.client.post(url, format='json', data=req_data)
        data = response.data
        print(data)
        self.assertEqual(400, response.status_code)

    def test_clinic_create_3(self):
        # все норм

        url = reverse('chat_create')

        req_data = {
            'user_ids': [],
            'center_ids': [1],
        }
        response = self.client.post(url, format='json', data=req_data)
        data = response.data
        print(data)
        self.assertEqual(400, response.status_code)
