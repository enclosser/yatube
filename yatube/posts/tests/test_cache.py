import time

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User


HOMEPAGE_URL = reverse('index')
USERNAME = 'test'
FIRST_POST_TEXT = 'Тестовый текст первого поста'
CACHE_POST_TEXT = 'Тестовый текст поста'


class CacheTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.post = Post.objects.create(
            text=FIRST_POST_TEXT,
            author=cls.user,
        )

    def setUp(self):
        self.client = Client()

    def test_cache(self):
        """Кэширование работает правильно."""
        response = self.client.get(HOMEPAGE_URL)
        self.assertEqual(len(response.context.get('page').object_list), 1)
        Post.objects.create(
            text=CACHE_POST_TEXT,
            author=CacheTest.user,
        )
        response = self.client.get(HOMEPAGE_URL)
        self.assertEqual(len(response.context.get('page').object_list), 1)
        time.sleep(20)
        response = self.client.get(HOMEPAGE_URL)
        self.assertEqual(len(response.context.get('page').object_list), 2)
        Post.objects.create(
            text=CACHE_POST_TEXT,
            author=CacheTest.user,
        )
        response = self.client.get(HOMEPAGE_URL)
        self.assertEqual(len(response.context.get('page').object_list), 2)
        cache.clear()
        response = self.client.get(HOMEPAGE_URL)
        self.assertEqual(len(response.context.get('page').object_list), 3)
