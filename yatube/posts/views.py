from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from utils import pagination
from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


def index(request):
    post_list = Post.objects.select_related('group').all()
    context = pagination(post_list, request)
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'group': group,
    }
    context.update(pagination(post_list, request))
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=author)
    posts_count = author.posts.count()
    context = {
        'author': author,
        'posts_count': posts_count,
    }
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author
        ).exists()
        context.update({'following': following, })
    context.update(pagination(post_list, request))
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post_obj = get_object_or_404(Post, id=post_id)
    post_count = Post.objects.filter(author=post_obj.author).count()
    current_user = request.user
    form = CommentForm(request.POST or None)
    comments = post_obj.comments.all()
    context = {
        'post_id': post_id,
        'post_obj': post_obj,
        'post_count': post_count,
        'current_user': current_user,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    is_edit = False
    form = PostForm(request.POST or None, files=request.FILES or None,)
    if form.is_valid():
        post_inst = form.save(commit=False)
        post_inst.author = request.user
        post_inst.save()
        return redirect('posts:profile', request.user)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'is_edit': is_edit}
    )


@login_required
def post_edit(request, post_id):
    post_inst = get_object_or_404(Post, id=post_id)
    if not request.user == post_inst.author:
        return redirect('posts:post_detail', post_id)
    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post_inst
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'post_id': post_id, 'is_edit': is_edit}
    )


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    followings = Follow.objects.values('author').filter(
        user=request.user)
    post_list = Post.objects.filter(author__in=followings)
    context = pagination(post_list, request)
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        new_following, created = Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(user=request.user, author=author).exists():
        new_unfollowing = get_object_or_404(
            Follow.objects,
            user=request.user,
            author=author
        )
        new_unfollowing.delete()
    return redirect('posts:follow_index')
