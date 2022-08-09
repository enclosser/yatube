from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages_accessible_by_name(self):
        """URLы, генерируемые при помощи имен  доступны."""
        list_of_names = [reverse('about:author'), reverse('about:tech')]
        for name in list_of_names:
            with self.subTest(name=name):
                response = self.guest_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_pages_uses_correct_template(self):
        """При запросе к about:author и about:tech
        применяются соответствующие шаблоны."""

        templates_url_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
