from django.test import TestCase

from posts.models import Comment, Group, Follow, Post, User


USER = 'test_user'
AUTHOR = 'test_author'
GROUP_TITLE = 'test_group'
GROUP_SLUG = 'test_slug'
GROUP_DESCRIPTION = 'test_description'
POST_TEXT = 'Тестовый текст поста'
COMMENT_TEXT = 'Тестовый текст комментария'


class PostsModelTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER)
        cls.author = User.objects.create_user(username=AUTHOR)

        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user
        )
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
            description=GROUP_DESCRIPTION
        )
        cls.comment = Comment.objects.create(
            text=COMMENT_TEXT,
            author=cls.user,
            post=cls.post,
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def test_post_object_name(self):
        """Метод __str__  возвращает ожидаемое представление объекта."""
        post = PostsModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_group_object_name(self):
        """Метод __str__  возвращает ожидаемое представление объекта."""
        group = PostsModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_comment_object_name(self):
        """Метод __str__  возвращает ожидаемое представление объекта."""
        comment = PostsModelTest.comment
        expected_object_name = comment.text[:15]
        self.assertEqual(expected_object_name, str(comment))

    def test_follow_object_name(self):
        """Метод __str__  возвращает ожидаемое представление объекта."""
        follow = PostsModelTest.follow
        expected_object_name = f'{USER} followed {AUTHOR}'
        self.assertEqual(expected_object_name, str(follow))
