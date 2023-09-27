from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from django.urls import reverse
from api.models import Country, Center, Disease, Clinic, User, Group, News
from social.models import Chat, Message

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
    
        url = reverse('send_first_message')

        req_data = {
            'user_ids': [1,2],
            'center_ids': [1],
            'news_id': 1,
            'text': "test@yandex.ru",
            'user': 1
        }
        response = self.client.post(url, format='json', data=req_data)
        data = response.data
        print(data)
        self.assertEqual(200, response.status_code)
        chat = Chat.objects.get(id=1)
        self.assertEqual(chat.users.all()[0].id, req_data["user_ids"][0])
        self.assertEqual(chat.users.all()[1].id, req_data["user_ids"][1])
        self.assertEqual(chat.centers.all()[0].id, req_data["center_ids"][0])
        message = Message.objects.get(id=1)
        self.assertEqual(message.chat.id, data["chat"]["id"])
        self.assertEqual(message.news.id, req_data["news_id"])
        self.assertEqual(message.note, None)
        self.assertEqual(message.text, None)
        self.assertEqual(message.user, req_data["user"])
        self.assertEqual(message.center, None)

        