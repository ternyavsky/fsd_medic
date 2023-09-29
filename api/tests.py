from django.test import TestCase, Client
from . import models
from db import queries

# Create your tests here.


class TestSearch(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_get_search(self):
        res = self.client.get("/api/search")
        print(res.content)
        self.assertEqual(res.status_code, 200)
