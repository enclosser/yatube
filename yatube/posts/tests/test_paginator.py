from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User


HOMEPAGE_URL = reverse('index')
USERNAME = 'test'
TEST_POST_TEXT = 'Тестовый текст поста'


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)

    def setUp(self):
        self.client = Client()
        Post.objects.bulk_create(
            [
                Post(
                    text=TEST_POST_TEXT,
                    author=PaginatorViewsTest.user
                )
            ] * 11
        )
        cache.clear()

    def test_pages_contains_expected_count_of_records(self):
        """Пагинация работает правильно."""
        response = self.client.get(HOMEPAGE_URL)
        self.assertEqual(len(response.context.get('page').object_list), 10)
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 1)
