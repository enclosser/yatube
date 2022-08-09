"""Posts app views file"""
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.core.cache import cache

from .forms import CommentForm, PostForm
from .models import Group, Follow, Post, User


POST_EDIT = True
PAGINATE_BY = settings.PAGINATE_BY
CACHED_TIME = settings.CACHED_TIME


def index(request):
    """Displays to the home page all posts."""
    post_list = cache.get('post_list')
    if not post_list:
        post_list = Post.objects.select_related('group').all()
        cache.set('post_list', post_list, CACHED_TIME)
    paginator = Paginator(post_list, PAGINATE_BY)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Displays to the group's page all posts."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, PAGINATE_BY)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
        'group': group,
    }
    return render(request, 'posts/group.html', context)


@login_required
def new_post(request):
    """Displays new post add form."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        new = form.save(commit=False)
        new.author = request.user
        new.save()
        return redirect(reverse('index'))
    context = {
        'form': form,
    }
    return render(request, 'posts/new_post.html', context)


def profile(request, username):
    """Displays given user's profile."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, PAGINATE_BY)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'author': author,
        'page': page,
    }
    return render(request, 'posts/profile.html', context)


def post_view(request, username, post_id):
    """Displays post with id."""
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    form = CommentForm()
    context = {
        'post': post,
        'author': author,
        'form': form,
    }
    return render(request, 'posts/post.html', context)


@login_required
def add_comment(request, username, post_id):
    """Displays new comment add form."""
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=author)
    form = CommentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.post = post
        new_comment.save()
        return redirect(reverse('post', args=(username, post_id)))
    context = {
        'post': post,
        'author': author,
        'form': form,
    }
    return render(request, 'posts/post.html', context)


def post_edit(request, username, post_id):
    """Displays edit form for post with id."""
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, pk=post_id, author=user)
    if username != request.user.username:
        return redirect(reverse('post', args=(username, post_id)))

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect(reverse('post', args=(username, post_id)))
    context = {
        'form': form,
        'post_edit': POST_EDIT,
        'post': post
    }
    return render(request, 'posts/new_post.html', context)


@login_required
def profile_follow(request, username):
    """To follow author with username."""
    author = get_object_or_404(User, username=username)
    follower_exists = request.user.follower.filter(author=author).exists()
    if follower_exists or author.id == request.user.id:
        return redirect('index')
    Follow.objects.create(user=request.user, author=author)
    return redirect('follow_index')


@login_required
def profile_unfollow(request, username):
    """To unfollow author with username."""
    author = get_object_or_404(User, username=username)
    follower_exists = request.user.follower.filter(author=author).exists()
    if not follower_exists or author.id == request.user.id:
        return redirect('index')
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('follow_index')


@login_required
def follow_index(request):
    """Displays posts of authors whom user follow."""

    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, PAGINATE_BY)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'page': page,
    }
    return render(request, 'posts/follow.html', context)


def page_not_found(request, exception):
    """Displays page not found error."""
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=HTTPStatus.NOT_FOUND
    )


def server_error(request):
    """Displays server error."""
    return render(
        request,
        'misc/500.html',
        status=HTTPStatus.INTERNAL_SERVER_ERROR
    )
