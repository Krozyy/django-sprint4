from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.forms import UserChangeForm
from .models import Post, Category, Comment
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .forms import PostForm
from .forms import CommentForm
from django.http import Http404
from django.db.models import Count

User = get_user_model()

def paginate(request, posts):
    paginat = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginat.get_page(page_number)
    return page_obj

def filtered():
    posts = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )
    return posts

def index(request):
    posts = filtered().annotate(comment_count = Count('comments')
    ).order_by('-pub_date')

    page_obj = paginate(request, posts)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = filtered().filter(category=category).annotate(comment_count = Count('comments')
    ).order_by('-pub_date')

    page_obj = paginate(request, posts)

    return render(request,
                  'blog/category.html',
                  {'category': category,
                   'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        category__is_published=True,
    )
    if not post.is_published or post.pub_date > timezone.now():
        if request.user != post.author:
            raise Http404("Пост не найден")
    form = CommentForm()
    comments =post.comments.all()
    return render(request, 'blog/detail.html', {'post': post, 'form':form, 'comments':comments})

def Profile(request, username):
    user = get_object_or_404(User, username = username)
    if request.user == user:
        posts = Post.objects.filter(author=user).annotate(comment_count = Count('comments')
    ).order_by('-pub_date')

    else:
         posts = filtered().filter(author=user).annotate(comment_count = Count('comments')
    ).order_by('-pub_date')

    page_obj = paginate(request, posts)

    context = {'profile':user, 'page_obj':page_obj,}
    return render(request, 'blog/profile.html', context)

@login_required
def edit_profile(request, username = None):
    if username is None:
        username = request.user.username

    if request.user.username != username:
        return redirect('blog:profile', username = request.user.username)
    
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance = request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username = request.user.username)
    else:
        form = UserChangeForm(instance=request.user)
        return render(request, 'blog/user.html', {'form':form})

def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = PostForm()
    
    return render(request, 'blog/create.html', {'form': form})

def edit_post(request, post_id):
    post = get_object_or_404(Post,id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    
    if request.method == 'POST':
        form =  PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form':form})

def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': PostForm(instance=post)})

def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    
    return redirect('blog:post_detail', post_id=post_id)

def edit_comment(request, post_id, comment_id):
    comment =get_object_or_404(Comment, id = comment_id, post_id = post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    context = {
        'form': form,
        'comment': comment,
    }
    return render(request, 'blog/comment.html', {'form':form, 'comment':comment})

def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id = comment_id, post_id = post_id)
    if comment.author == request.user:
        comment.delete()
        return redirect('blog:post_detail', post_id = post_id)
    
    return render(request, 'blog/comment.html',{'comment':comment})

def password_change(request):
    return redirect('password_change')