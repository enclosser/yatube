from django.contrib import admin

from .models import Comment, Group, Follow, Post


EMPTY_VALUE = '-пусто-'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Represents the model Post in admin interface."""
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = EMPTY_VALUE


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Represents the model Group in admin interface."""
    list_display = ('pk', 'title', 'slug', 'description')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Represents the model Comment in admin interface."""
    list_display = ('pk', 'text', 'author', 'post', 'created')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Represents the model Follow in admin interface."""
    list_display = ('pk', 'user', 'author')
