from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Count
from django.views.generic import (
    CreateView, DeleteView, ListView, UpdateView, DetailView
)
from django.urls import reverse, reverse_lazy
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
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
    pk_url_kwarg = 'post_id'
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = get_object_or_404(Post, id=self.kwargs['post_id'])
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
    posts = None
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            raise Http404('Error')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
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
    pk_url_kwarg = 'post_id'
    form_class = PostForm
    template_name = 'blog/create.html'

    def dispatch(self, request, *args, **kwargs):
        post_pk = get_object_or_404(Post, id=self.kwargs['post_id'])
        if self.request.user != post_pk.author:
            return redirect(
                'blog:post_detail', post_pk.id
            )
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
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args, **kwargs):
        author = request.user
        if author != request.user:
            return redirect('blog:index', id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = get_object_or_404(Post, pk=self.kwargs['post_id'])
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
        self.post_ = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post_ = self.post_
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.post_.pk}
        )


# Изменение комментария
class CommentUpdateView(LoginRequiredMixin, UpdateView):
    posts = None
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.posts.pk}
        )


# Удаление комментария
class CommentDeleteView(LoginRequiredMixin, DeleteView):
    posts = None
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = {'instance': self.object}
        return context

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.posts.pk}
        )
