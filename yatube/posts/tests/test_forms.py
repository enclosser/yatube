import shutil
import tempfile

from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User
from posts.forms import PostForm


HOMEPAGE_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
USERNAME = 'test'
TEST_POST_TEXT = 'Тестовый текст поста'
FORM_POST_TEXT = 'Тестовый текст поста через форму'
EDIT_POST_TEXT = 'Редактированный текст поста через форму'
EMPTY_TEXT = ''
ERROR_MSG = 'Обязательное поле.'
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
EDIT_IMAGE_NAME = 'edit_image.gif'
EDIT_IMAGE_URL = f'posts/{EDIT_IMAGE_NAME}'
CONTENT_TYPE = 'image/gif'


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username=USERNAME)
        cls.post = Post.objects.create(
            text=TEST_POST_TEXT,
            author=cls.user,
        )
        cls.form = PostForm()
        cls.POST_URL = reverse(
            'post',
            args=(cls.user.username, cls.post.id)
        )
        cls.POST_EDIT_URL = reverse(
            'post_edit',
            args=(cls.user.username, cls.post.id)
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTest.user)

    def test_post_create(self):
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name=IMAGE_NAME,
            content=SMALL_GIF,
            content_type=CONTENT_TYPE
        )
        form_data = {
            'text': FORM_POST_TEXT,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, HOMEPAGE_URL)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_created_post = Post.objects.first()
        self.assertEqual(last_created_post.text, form_data['text'])
        self.assertEqual(last_created_post.author, PostFormTest.user)
        self.assertEqual(last_created_post.group, form_data.get('group'))
        self.assertEqual(last_created_post.image, IMAGE_URL)

    def test_cant_create_empty_text(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': EMPTY_TEXT,
        }
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFormError(response, 'form', 'text', ERROR_MSG)

    def test_edit_post(self):
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name=EDIT_IMAGE_NAME,
            content=SMALL_GIF,
            content_type=CONTENT_TYPE
        )
        form_data = {
            'text': EDIT_POST_TEXT,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            PostFormTest.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            PostFormTest.POST_URL
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.context['post'].text, EDIT_POST_TEXT)
        self.assertEqual(response.context['post'].image, EDIT_IMAGE_URL)
