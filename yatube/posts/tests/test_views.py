import shutil
import tempfile

from django import forms
from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User


FIRST_GROUP_TITLE = 'test_group_first'
FIRST_GROUP_SLUG = 'test_slug_first'
GROUP_DESCRIPTION = 'test_description'
SECOND_GROUP_TITLE = 'test_group_second'
SECOND_GROUP_SLUG = 'test_slug_second'
FIRST_GROUP_POST_TEXT = 'Тестовый текст поста первой группы'
SECOND_GROUP_POST_TEXT = 'Тестовый текст поста второй группы'
TEST_USERNAME = 'test'
FOLLOWING_AUTHOR = 'test2'
FOLLOWING_AUTHOR_TEXT = 'test test test'
HOMEPAGE_URL = reverse('index')
GROUP_FIRST_URL = reverse('group_posts', args=(FIRST_GROUP_SLUG,))
GROUP_SECOND_URL = reverse('group_posts', args=(SECOND_GROUP_SLUG,))
NEW_POST_URL = reverse('new_post')
FOLLOW_URL = reverse('follow_index')
PROFILE_URL = reverse('profile', args=(TEST_USERNAME,))
AUTHOR_FOLLOW_URL = reverse('profile_follow', args=(FOLLOWING_AUTHOR,))
AUTHOR_UNFOLLOW_URL = reverse('profile_unfollow', args=(FOLLOWING_AUTHOR,))
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
IMAGE_NAME = 'small.gif'
IMAGE_URL = f'posts/{IMAGE_NAME}'
CONTENT_TYPE = 'image/gif'


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.uploaded = SimpleUploadedFile(
            name=IMAGE_NAME,
            content=SMALL_GIF,
            content_type=CONTENT_TYPE
        )
        cls.user = User.objects.create_user(username=TEST_USERNAME)
        cls.following_author = User.objects.create_user(
            username=FOLLOWING_AUTHOR
        )

        cls.group_1 = Group.objects.create(
            title=FIRST_GROUP_TITLE,
            slug=FIRST_GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.group_2 = Group.objects.create(
            title=SECOND_GROUP_TITLE,
            slug=SECOND_GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.post_1 = Post.objects.create(
            text=FIRST_GROUP_POST_TEXT,
            author=cls.user,
            group=cls.group_1,
            image=cls.uploaded
        )
        cls.post_2 = Post.objects.create(
            text=SECOND_GROUP_POST_TEXT,
            author=cls.user,
            group=cls.group_2,
            image=cls.uploaded
        )
        cls.POST_URL = reverse(
            'post',
            args=(TEST_USERNAME, PostsPagesTests.post_1.id)
        )
        cls.POST_EDIT_URL = reverse(
            'post_edit',
            args=(TEST_USERNAME, PostsPagesTests.post_1.id)
        )
        cls.POST_COMMENT_URL = reverse(
            'add_comment',
            args=(TEST_USERNAME, PostsPagesTests.post_1.id)
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsPagesTests.user)
        self.other_authorized = Client()
        self.other_authorized.force_login(PostsPagesTests.following_author)
        cache.clear()

    def test_posts_pages_accessible_by_name(self):
        """URLы, генерируемые при помощи имен  доступны."""
        list_of_names = [
            HOMEPAGE_URL,
            GROUP_FIRST_URL,
            NEW_POST_URL,
        ]
        for name in list_of_names:
            with self.subTest(name=name):
                response = self.authorized_client.get(name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_views_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_url_names = {
            'posts/index.html': HOMEPAGE_URL,
            'posts/group.html': GROUP_FIRST_URL,
            'posts/new_post.html': NEW_POST_URL,
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_home_page_shows_correct_context(self):
        """Шаблон главной страницы сформирован с правильным контекстом."""
        response = self.authorized_client.get(HOMEPAGE_URL)
        first_object = response.context['page'].object_list[0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, PostsPagesTests.post_2.text)
        self.assertEqual(post_author_0, PostsPagesTests.user)
        self.assertEqual(post_group_0, PostsPagesTests.post_2.group)
        self.assertEqual(post_image_0, PostsPagesTests.post_2.image)

    def test_group_page_shows_correct_context(self):
        """Шаблон /group/test_slug_second/ сформирован с правильным контекстом.
        """
        response = self.authorized_client.get(GROUP_SECOND_URL)
        group_slug = response.context.get('group').slug
        page_object_list = response.context.get('page').object_list
        posts_count = len(page_object_list)
        first_object = page_object_list[0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_pub_date_0 = first_object.pub_date
        post_group_0 = first_object.group
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, PostsPagesTests.post_2.text)
        self.assertEqual(post_author_0, PostsPagesTests.user)
        self.assertEqual(post_pub_date_0, PostsPagesTests.post_2.pub_date)
        self.assertEqual(post_group_0, PostsPagesTests.post_2.group)
        self.assertEqual(post_image_0, PostsPagesTests.post_2.image)
        self.assertEqual(group_slug, PostsPagesTests.group_2.slug)
        self.assertEqual(posts_count, 1)
        response = self.authorized_client.get(GROUP_FIRST_URL)
        page_object_list = response.context.get('page').object_list
        first_object = page_object_list[0]
        post_group = first_object.group
        self.assertNotEqual(post_group, PostsPagesTests.group_2)

    def test_new_post_page_shows_correct_context(self):
        """Шаблон создания нового поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(NEW_POST_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_page_shows_correct_context(self):
        """Шаблон просмотра профиля сформирован с правильным контекстом."""
        response = self.authorized_client.get(PROFILE_URL)
        first_object = response.context['page'].object_list[0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_pub_date_0 = first_object.pub_date
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, PostsPagesTests.post_2.text)
        self.assertEqual(post_author_0, PostsPagesTests.user)
        self.assertEqual(post_pub_date_0, PostsPagesTests.post_2.pub_date)
        self.assertEqual(post_image_0, PostsPagesTests.post_2.image)

    def test_post_page_shows_correct_context(self):
        """Шаблон просмотра поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(PostsPagesTests.POST_URL)
        post = response.context['post']
        post_text = post.text
        post_author = post.author
        post_pub_date = post.pub_date
        post_image = post.image
        post_group = post.group

        self.assertEqual(post_text, PostsPagesTests.post_1.text)
        self.assertEqual(post_author, PostsPagesTests.user)
        self.assertEqual(post_pub_date, PostsPagesTests.post_1.pub_date)
        self.assertEqual(post_image, PostsPagesTests.post_1.image)
        self.assertEqual(post_group, PostsPagesTests.post_1.group)

    def test_post_edit_page_shows_correct_context(self):
        """Шаблон редактирования поста сформирован с правильным контекстом."""
        response = self.authorized_client.get(PostsPagesTests.POST_EDIT_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
        form_data = {
            'text': FIRST_GROUP_POST_TEXT,
            'group': PostsPagesTests.group_1.id,
            'image': IMAGE_URL,
        }
        for field, data in form_data.items():
            with self.subTest(value=field):
                form_field = response.context['form'][field].value()
                self.assertEqual(form_field, data)

    def test_following_and_unfollowing_pages(self):
        followers = PostsPagesTests.user.follower.count()
        response = self.authorized_client.get(AUTHOR_FOLLOW_URL)
        self.assertRedirects(response, FOLLOW_URL)
        self.assertEqual(PostsPagesTests.user.follower.count(), followers + 1)
        Post.objects.create(
            text=FOLLOWING_AUTHOR_TEXT,
            author=PostsPagesTests.following_author
        )
        response = self.authorized_client.get(FOLLOW_URL)
        post = response.context['page'].object_list[0]
        self.assertEqual(post.text, FOLLOWING_AUTHOR_TEXT)
        self.assertEqual(post.author, PostsPagesTests.following_author)

        response = self.other_authorized.get(FOLLOW_URL)
        page = response.context.get('page')
        if page:
            self.assertNotEqual(
                page.object_list[0].post.text,
                FOLLOWING_AUTHOR_TEXT
            )
            self.assertNotEqual(
                page.object_list[0].post.author,
                PostsPagesTests.following_author
            )

        response = self.authorized_client.get(AUTHOR_UNFOLLOW_URL)
        self.assertRedirects(response, FOLLOW_URL)
        self.assertEqual(PostsPagesTests.user.follower.count(), followers)
