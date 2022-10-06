from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Group, Post, User, Follow
from .forms import CommentForm, PostForm
from .paginator import paginator


def index(request):
    post_list = (Post
                 .objects
                 .prefetch_related())
    page_obj = paginator(request, post_list)
    return render(request, 'posts/index.html', {'page_obj': page_obj})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = (Post
                 .objects
                 .filter(group=group)
                 .prefetch_related())
    page_obj = paginator(request, post_list)
    return render(request,
                  'posts/group_list.html',
                  {'group': group, 'page_obj': page_obj}
                )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        following = request.user.follower.filter(author=author).exists()
    post_list = (Post
                 .objects
                 .filter(author=author)
                 .prefetch_related())
    page_obj = paginator(request, post_list)
    return render(request,
                  'posts/profile.html',
                  {'author': author,
                  'page_obj': page_obj,
                  'following': following}
                )


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_list = (Post
                 .objects
                 .filter(author=post.author)
                 .prefetch_related())
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    return render(request,
                  'posts/post_detail.html',
                  {'post_count': post_list,
                   'post': post,
                   'form': form,
                   'comments': comments}
                )


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user.username)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:profile', username=request.user.username)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request,
                  'posts/create_post.html',
                  {'form': form,
                  'post': post,
                  'is_edit': True}
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
    title = 'Публикации избранных авторов'
    post_list = (Post
                 .objects
                 .filter(author__following__user=request.user)
                 .prefetch_related())
    page_obj = paginator(request, post_list)
    return render(request,
                  'posts/follow.html',
                  {'title': title,
                  'page_obj': page_obj}
                )


@login_required
def profile_follow(request, username):
    follow_author = get_object_or_404(User, username=username)
    if follow_author != request.user and (
        not request.user.follower.filter(author=follow_author).exists()
    ):
        Follow.objects.create(
            user=request.user,
            author=follow_author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    follow_author = get_object_or_404(User, username=username)
    data_follow = request.user.follower.filter(author=follow_author)
    if data_follow.exists():
        data_follow.delete()
    return redirect('posts:profile', username)
