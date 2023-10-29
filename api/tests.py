# Create your tests here.
from rest_framework.test import APIRequestFactory
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient, force_authenticate
from .views import LikeViewSet, SaveViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import *
from django.test import TestCase


class LikeViewsetTestCase(TestCase):

    def setUp(self):
        Group.objects.create(name="Пользователи")
        News.objects.create(title="Test title")
        City.objects.create(name="Москва")
        Country.objects.create(name="Россия")
        User.objects.create(
            number="+79991119911", 
            password="test",
            group=Group.objects.get(id=1),
            country=Country.objects.get(id=1),
            city=City.objects.get(id=1))
        self.client = Client()
        self.request = APIRequestFactory()
    
    def test_like_viewset_get(self):
        request = self.request.get("")
        view = LikeViewSet.as_view({"get": "retrieve"})
        like = Like(user=User.objects.get(id=1), news=News.objects.get(id=1))
        like.save()
        token = RefreshToken.for_user(User.objects.get(id=1))
        force_authenticate(request, user=User.objects.get(id=1))
        response = view(request, pk=like.pk)
        self.assertEqual(response.status_code, 200)


    # def test_like_viewset_create(self):
    #     request = self.request.post("")
    #     view = LikeViewSet.as_view({""})


class SaveViewsetTestCase(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name="Пользователи")
        self.news = News.objects.create(title="Test title")
        self.city = City.objects.create(name="Москва")
        self.country = Country.objects.create(name="Россия")
        self.user = User.objects.create(
            number="+79991119911", 
            password="test",
            group=self.group,
            country=self.country,
            city=self.city)
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.request = APIRequestFactory()
    
    def test_save_viewset_get(self):
        request = self.request.get("")
        view = SaveViewSet.as_view({"get": "retrieve"})
        saved = Saved(user=self.user, news=self.news)
        saved.save()
        token = RefreshToken.for_user(self.user)
        force_authenticate(request, user=self.user)
        response = view(request, pk=saved.pk)
        self.assertEqual(response.status_code, 200)


    def test_save_viewset_post(self):
        url = reverse("saved-list")
        view = SaveViewSet.as_view({"post": "create"})
        data = {
            "news": self.news.id,
            "user": self.user.id
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, 201)
