from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView, DetailView
)
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone

from .models import Post, Category, Comment, User
from .forms import PostForm, CommentForm


# Главная страница
def index(request):
    post_list = Post.objects.filter(
        pub_date__date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).annotate(comment_count=Count('comments')
               ).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'blog/index.html', {'page_obj': page_obj})


# Описание поста
class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    form_class = PostForm
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=self.kwargs['pk'])
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        context['form'] = CommentForm()
        return context


# Страница категории
def category_posts(request, category_slug):
    post_list = Post.objects.select_related(
        'category', 'location', 'author').filter(
        category__slug=category_slug,
        is_published=True,
        pub_date__date__lte=timezone.now()
    ).annotate(comment_count=Count('comments')
               ).order_by('-pub_date')
    category = get_object_or_404(
        Category.objects.filter(
            is_published=True
        ),
        slug=category_slug
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj,
               'category': category}
    return render(request, 'blog/category.html', context)


# Страница пользователя
class ProfileListView(ListView):
    model = Post
    pk_url_kwarg = 'username'
    template_name = 'blog/profile.html'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        if self.request.user.username == self.kwargs['username']:
            return Post.objects.select_related('author').filter(
                author__username=self.kwargs['username']
            ).annotate(comment_count=Count('comments')
                       ).order_by('-pub_date')
        return Post.objects.select_related('author').filter(
            author__username=self.kwargs['username'],
            pub_date__lte=timezone.now()
        ).annotate(comment_count=Count('comments')
                   ).order_by('-pub_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.user
        return context

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy(
            'blog:profile',
            args=[username]
        )


# Изменение профиля
class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    pk_url_kwarg = 'username'
    fields = '__all__'
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy(
            'blog:profile',
            args=[username]
        )


# Создание поста
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        if form.instance.pub_date > timezone.now():
            form.instance.is_published = False
        else:
            form.instance.is_published = True
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy(
            'blog:profile',
            args=[username]
        )


# Изменение поста
class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post_ = get_object_or_404(Post, pk=self.kwargs['pk'])
        if self.request.user != post_.author:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy(
            'blog:profile',
            args=[username]
        )


# Удаление поста
class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        # author = request.user
        instance = get_object_or_404(Post, pk=self.kwargs['pk'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs['pk'])
        context['form'] = {'instance': instance}
        return context

    def get_success_url(self):
        username = self.request.user.username
        return reverse_lazy(
            'blog:profile',
            args=[username]
        )


# Создание комментария
class CommentCreateView(LoginRequiredMixin, CreateView):
    post_ = None
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post_ = get_object_or_404(Post, pk=self.kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail', kwargs={'pk': self.object.post.id})


# Изменение комментария
class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)


# Удаление комментария
class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['pk'])
        return super().dispatch(request, *args, **kwargs)
