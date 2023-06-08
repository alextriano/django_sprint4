from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


User = get_user_model()


class Category(models.Model):
    title = models.CharField(
        max_length=256,
        blank=True,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание'
    )
    slug = models.SlugField(
        unique=True,
        blank=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; '
        'разрешены символы латиницы, цифры, дефис и подчёркивание.'
    )
    is_published = models.BooleanField(
        default=True,
        blank=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Добавлено')

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title[:10]


class Location(models.Model):
    name = models.CharField(
        max_length=256,
        blank=True,
        verbose_name='Название места'
    )
    is_published = models.BooleanField(
        default=True,
        blank=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Добавлено'
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'


class Post(models.Model):
    title = models.CharField(
        max_length=256,
        blank=True,
        verbose_name='Заголовок'
    )
    text = models.TextField(
        blank=True,
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        blank=True,
        verbose_name='Дата и время публикации',
        help_text='Если установить дату и время в будущем — '
        'можно делать отложенные публикации.'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        blank=True,
        verbose_name='Автор публикации'
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=False,
        verbose_name='Местоположение'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория'
    )
    is_published = models.BooleanField(
        default=True,
        blank=True,
        verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        blank=True,
        verbose_name='Добавлено'
    )
    image = models.ImageField(
        'Фото',
        upload_to='posts_images',
        blank=True
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})


class Comment(models.Model):
    text = models.TextField(
        'Текст комментария',
        blank=False,
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        verbose_name='Автор комментария'
    )
    post = models.ForeignKey(
        Post,
        blank=False,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at',)
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.title
