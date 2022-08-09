from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


USERNAME = 'username'
FOLLOWING_USERNAME = 'username2'
NON_EXISTENT = 'non-existent'
NOT_AUTHOR_USERNAME = 'not_author'
GROUP_TITLE = 'test_group'
GROUP_SLUG = 'test_slug'
GROUP_DESCRIPTION = 'test_description'
POST_TEXT = 'Тестовый текст поста'
HOMEPAGE_URL = '/'
NEW_POST_URL = '/new/'
FOLLOW_URL = '/follow/'
GROUP_URL = f'/group/{GROUP_SLUG}/'
PROFILE_URL = f'/{USERNAME}/'
AUTHOR_FOLLOW_URL = f'/{FOLLOWING_USERNAME}/follow/'
AUTHOR_UNFOLLOW_URL = f'/{FOLLOWING_USERNAME}/unfollow/'
URL_FOR_404 = f'/{NON_EXISTENT}/'


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_not_author = User.objects.create_user(
            username=NOT_AUTHOR_USERNAME
        )
        cls.user_following = User.objects.create_user(
            username=FOLLOWING_USERNAME
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
            group=cls.group,
        )
        cls.POST_URL = f'/{USERNAME}/{cls.post.id}/'
        cls.POST_EDIT_URL = f'/{USERNAME}/{cls.post.id}/edit/'
        cls.POST_COMMENT_URL = f'/{USERNAME}/{cls.post.id}/comment/'

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)
        self.authorized_client_not_author = Client()
        self.authorized_client_not_author.force_login(
            PostsURLTests.user_not_author
        )
        cache.clear()

    def test_non_existent_url_responses_404(self):
        """Если страница не существует, возвращается код 404"""
        response = self.guest_client.get(URL_FOR_404, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_exists_at_desired_location(self):
        """Страницы доступные любому пользователю."""
        url_names = [
            HOMEPAGE_URL,
            GROUP_URL,
            PROFILE_URL,
            PostsURLTests.POST_URL,
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exists_at_desired_location_authorized(self):
        """
        Страницы нового поста, постов подписок и комментирования поста доступны
        авторизованному пользователю.
        """
        url_names = [
            NEW_POST_URL,
            FOLLOW_URL,
            PostsURLTests.POST_COMMENT_URL,
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_authorized(self):
        """
        Страницы подписки и отписки редиректят авторизованного пользователя.
        """
        url_names = [
            AUTHOR_FOLLOW_URL,
            AUTHOR_UNFOLLOW_URL,
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_urls_for_authorized_redirect_anonymous_on_admin_login(self):
        """Страницы для авторизованных пользователей перенаправят анонимного
        пользователя на страницу логина.
        """
        urls = [
            NEW_POST_URL,
            FOLLOW_URL,
            AUTHOR_FOLLOW_URL,
            AUTHOR_UNFOLLOW_URL,
            PostsURLTests.POST_COMMENT_URL,
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(
                    response,
                    (reverse('login') + '?next=' + url)
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            HOMEPAGE_URL: 'posts/index.html',
            GROUP_URL: 'posts/group.html',
            NEW_POST_URL: 'posts/new_post.html',
            PROFILE_URL: 'posts/profile.html',
            FOLLOW_URL: 'posts/follow.html',
            PostsURLTests.POST_URL: 'posts/post.html',
            PostsURLTests.POST_EDIT_URL: 'posts/new_post.html',
            PostsURLTests.POST_COMMENT_URL: 'posts/post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_unavailable_to_unauthorized(self):
        """Страница /username/post_id/edit/ недоступна не авторизованному
        клиенту.
        """
        response = self.guest_client.get(reverse(
            'post_edit',
            args=(PostsURLTests.user.username, PostsURLTests.post.id)
        ))
        self.assertNotEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'post',
            args=(PostsURLTests.user.username, PostsURLTests.post.id)
        ))

    def test_post_edit_url_unavailable_to_authorized_not_author(self):
        """Страница /username/post_id/edit/ недоступна авторизованному
         не автору поста.
        """
        response = self.authorized_client_not_author.get(reverse(
            'post_edit',
            args=(PostsURLTests.user.username, PostsURLTests.post.id)
        ))
        self.assertNotEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response, reverse(
            'post',
            args=(PostsURLTests.user.username, PostsURLTests.post.id)
        ))

    def test_post_edit_url_available_to_authorized_author(self):
        """Страница /username/post_id/edit/ доступна авторизованному
        автору поста.
        """
        response = self.authorized_client.get(reverse(
            'post_edit',
            args=(PostsURLTests.user.username, PostsURLTests.post.id)
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)
