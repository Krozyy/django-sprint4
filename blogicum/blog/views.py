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

User = get_user_model()

def index(request):
    posts = Post.objects.filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')

    paginat = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginat.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    posts = Post.objects.filter(
        category=category,
        is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-pub_date')

    paginat = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginat.get_page(page_number)

    return render(request,
                  'blog/category.html',
                  {'category': category,
                   'page_obj': page_obj})


def post_detail(request, pk):
    post = get_object_or_404(
        Post,
        pk=pk,
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
        posts = Post.objects.filter(author=user).order_by('-pub_date')
    else:
        posts = Post.objects.filter(
            author=user,
            is_published=True,
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')

    paginat = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginat.get_page(page_number)

    context = {'profile':user, 'page_obj':page_obj,}
    return render(request, 'blog/profile.html', context)

@login_required
def edit_profile(request, username):
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

def edit_profile_red(request):
    return redirect('blog:edit_profile', username=request.user.username)

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

def edit_post(request, pk):
    post = get_object_or_404(Post,pk=pk)
    if post.author != request.user:
        return redirect('blog:post_detail', pk=pk)
    
    if request.method == 'POST':
        form =  PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/create.html', {'form':form})

def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('blog:post_detail', pk=pk)
    
    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', username=request.user.username)
    return render(request, 'blog/create.html', {'form': PostForm(instance=post)})

def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    
    return redirect('blog:post_detail', pk=post_id)

def edit_comment(request, post_id, comment_id):
    comment =get_object_or_404(Comment, pk = comment_id, post_id = post_id)
    if comment.author != request.user:
        return redirect('blog:post_detail', pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', pk=post_id)
    else:
        form = CommentForm(instance=comment)

    context = {
        'form': form,
        'comment': comment,
    }
    return render(request, 'blog/comment.html', {'form':form, 'comment':comment})

def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk = comment_id, post_id = post_id)
    if comment.author == request.user:
        comment.delete()
        return redirect('blog:post_detail', pk = post_id)
    
    return render(request, 'blog/comment.html',{'comment':comment})

def password_change(request, username):
    return redirect('password_change')