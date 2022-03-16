from django.core import paginator
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Blog, Tag
from .forms import BlogForm, CommentForm
from .utils import searchBlogs, paginateBlogs


def blogs(request):
    blogs, search_query = searchBlogs(request)
    custom_range, blogs = paginateBlogs(request, blogs, 3)

    context = {'blogs': blogs,
               'search_query': search_query, 'custom_range': custom_range}
    return render(request, 'blog/blogs.html', context)


def blog(request, pk):
    blogObj = Blog.objects.get(id=pk)
    form = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        comment = form.save(commit=False)
        comment.blog = blogObj
        comment.owner = request.user.profile
        comment.save()

        messages.success(request, 'Your comment was successfully submitted!')
        return redirect('blog', pk=blogObj.id)

    return render(request, 'blog/single-blog.html', {'blog': blogObj, 'form': form})


@login_required(login_url="login")
def createBlog(request):
    profile = request.user.profile
    form = BlogForm()

    if request.method == 'POST':
        newtags = request.POST.get('newtags').replace(',',  " ").split()
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.owner = profile
            blog.save()

            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                blog.tags.add(tag)
            return redirect('account')

    context = {'form': form}
    return render(request, "blog/blog_form.html", context)


@login_required(login_url="login")
def updateBlog(request, pk):
    profile = request.user.profile
    blog = profile.blog_set.get(id=pk)
    form = BlogForm(instance=blog)

    if request.method == 'POST':
        newtags = request.POST.get('newtags').replace(',',  " ").split()

        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            blog = form.save()
            for tag in newtags:
                tag, created = Tag.objects.get_or_create(name=tag)
                blog.tags.add(tag)

            return redirect('account')

    context = {'form': form, 'blog': blog}
    return render(request, "blog/blog_form.html", context)


@login_required(login_url="login")
def deleteBlog(request, pk):
    profile = request.user.profile
    blog = profile.blog_set.get(id=pk)
    if request.method == 'POST':
        blog.delete()
        return redirect('blog')
    context = {'object': blog}
    return render(request, 'delete_template.html', context)
