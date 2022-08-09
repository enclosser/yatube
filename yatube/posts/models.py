from django.contrib.auth import get_user_model
from django.db import models

from .validators import validate_not_empty


User = get_user_model()


class Group(models.Model):
    """Presents model of group in blog."""
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField('Слаг', unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self):
        return self.title


class Post(models.Model):
    """Presents model of post in blog."""
    text = models.TextField('Текст поста', validators=[validate_not_empty])
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        verbose_name='Сообщество',
        blank=True,
        null=True
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True,
        null=True
    )

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'posts'
        verbose_name = 'post'
        verbose_name_plural = 'posts'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """Represent model of comments."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(
        'Текст комментария',
        validators=[validate_not_empty]
    )
    created = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        ordering = ('-created',)
        default_related_name = 'comments'
        verbose_name = 'comment'
        verbose_name_plural = 'comments'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following')

    class Meta:
        unique_together = ('user', 'author')

    def __str__(self):
        return f'{self.user.username} followed {self.author.username}'
