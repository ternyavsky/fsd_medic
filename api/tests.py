# Create your tests here.
from rest_framework.test import APIRequestFactory
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient, force_authenticate
from .views import LikeViewSet, SaveViewSet, NoteViewSet, SearchView
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import *

from django.test import TestCase


# class SearchViewTest(TestCase):
#     def setUp(self):
#         self.factory = APIRequestFactory()
#         self.view = SearchView.as_view()
#         self.uri = "/api/search/"

#     def test_search_view(self):
#         request = self.factory.get(self.uri)
#         response = self.view(request)
#         self.assertEqual(response.status_code, 200)


# write test for likeviewset with apiclient and force_authenticate
class LikeViewSetTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = LikeViewSet.as_view({"post": "create"})
        self.uri = "/api/like/"

    def test_like_view(self):
        request = self.factory.post(self.uri)
        response = self.view(request)
        self.assertEqual(response.status_code, 401)
