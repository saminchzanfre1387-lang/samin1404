
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Post
from .forms import PostCreateUpdateForm
from.forms import PostCreateUpdateForm,CommentCreateForm
from django.utils.text import slugify

class HomView(View):
    def get(self, request):
        posts = Post.objects.all()
        return render(request, 'home/index.html', {'posts': posts})

    def post(self, request):
        posts = Post.objects.all()
        return render(request, 'home/index.html', {'posts': posts})


class PostDetailView(View):
    form_class=CommentCreateForm
    def get(self, request, post_id, post_slug):
        post = get_object_or_404(Post, pk=post_id, slug=post_slug)
        comments=post.pcomments.filter(is_reply=False)
        return render(request, 'home/detail.html', {'post': post,'comments':comments,'form':self.form_class})


class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if post.user == request.user:
            post.delete()
            messages.success(request, 'پست با موفقیت حذف شد.')
        else:
            messages.error(request, 'شما اجازه حذف این پست را ندارید.')
        return redirect('home:home')
class PostUpdateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def dispatch(self, request, *args, **kwargs):
        # اینجا post_instance را مقداردهی می‌کنیم
        self.post_instance = get_object_or_404(Post, pk=kwargs['post_id'])

        # بررسی مجوز کاربر
        if self.post_instance.user != request.user:
            messages.error(request, 'you cant update this post', 'danger')
            return redirect('home:home')

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.form_class(instance=self.post_instance)
        return render(request, 'home/update.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.post_instance)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.save()
            messages.success(request, 'you updated this post', 'success')
            return redirect('home:post_detail', post_id=new_post.id, post_slug=new_post.slug)
        return render(request, 'home/update.html', {'form': form})
class PostCreateView(LoginRequiredMixin, View):
    form_class = PostCreateUpdateForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, 'home/create.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.user = request.user
            new_post.save()
            messages.success(request, 'you created this post', 'success')
            return redirect('home:post_detail', post_id=new_post.id, post_slug=new_post.slug)
        return render(request, 'home/create.html', {'form': form})

