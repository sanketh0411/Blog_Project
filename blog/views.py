from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Blog,Comment

from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            print("Passwords do not match")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            print('Username already exists')
            return redirect('register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()
        return redirect('login')

    return render(request, 'register.html')


def user_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            # messages.error(request, "Invalid credentials")
            print("Invalid credentials")
            return redirect('login')

    return render(request, 'login.html')


@login_required
def create_blog(request):
    if request.method == "POST":
        title = request.POST['title']
        content = request.POST['content']

        Blog.objects.create(
            author=request.user,
            title=title,
            content=content
        )
        return redirect('home')

    return render(request, 'create_blog.html')

def home(request):
    blogs = Blog.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'blogs': blogs})

@login_required
def like_blog(request, blog_id):
    blog = Blog.objects.get(id=blog_id)

    if request.user in blog.likes.all():
        blog.likes.remove(request.user)
    else:
        blog.likes.add(request.user)

    return redirect('home')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if blog.author != request.user:
        return HttpResponseForbidden("You are not allowed")

    if request.method == "POST":
        blog.title = request.POST['title']
        blog.content = request.POST['content']
        blog.save()
        return redirect('home')

    return render(request, 'edit_blog.html', {'blog': blog})


@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if blog.author != request.user:
        return HttpResponseForbidden("You are not allowed")

    blog.delete()
    return redirect('home')


@login_required
def add_comment(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id)

    if request.method == "POST":
        Comment.objects.create(
            blog=blog,
            user=request.user,
            text=request.POST['comment']
        )

    return redirect('home')
