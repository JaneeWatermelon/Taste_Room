import os
from uuid import uuid4

from bs4 import BeautifulSoup
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import JSONField
from django.utils.text import slugify
from django.utils.timezone import now
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from additions.views import Status, Visibility, get_unique_slug
from categories.models import RecipeCategory
from users.models import User


def news_preview_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"image_{uuid4().hex}.{ext}"
    return os.path.join("news_previews", filename)

def news_comments_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"image_{uuid4().hex}.{ext}"
    return os.path.join("news_comments_images", filename)

class News(models.Model):
    title = models.CharField(max_length=128, verbose_name="Название")
    slug = models.SlugField(blank=True, default=slugify(title), verbose_name="Ссылочное название")
    preview = models.ImageField(upload_to=news_preview_image_path, verbose_name="Превью")
    optimized_image = ImageSpecField(
        source='preview',
        processors=[ResizeToFill(1536, 1024)],  # Размер оптимизированного изображения
        format='WebP',
        options={'quality': 85}
    )
    optimized_image_small = ImageSpecField(
        source='preview',
        processors=[ResizeToFill(525, 350)],  # Размер оптимизированного изображения
        format='WebP',
        options={'quality': 100}
    )
    description_card = models.CharField(max_length=64, verbose_name="Описание для карточки")

    content_start = RichTextUploadingField(config_name="awesome_ckeditor", verbose_name="Контент 1 часть")
    content_middle = models.TextField(default="", blank=True, null=True, verbose_name="Вставка")
    content_end = RichTextUploadingField(default="", blank=True, config_name="awesome_ckeditor", verbose_name="Контент 2 часть")
    headings = models.JSONField(default=list, blank=True, null=True, verbose_name="Содержание")

    rating = models.PositiveSmallIntegerField(default=0,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ], verbose_name="Рейтинг")
    published_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")

    status = models.PositiveSmallIntegerField(choices=Status.List, verbose_name="Статус")
    status_updated_at = models.DateTimeField(default=now, verbose_name="Время обновления статуса")
    visibility = models.PositiveSmallIntegerField(choices=Visibility.List, verbose_name="Видимость")
    popularity = models.PositiveSmallIntegerField(default=0, verbose_name="Популярность")

    categories = models.ManyToManyField(to=RecipeCategory, blank=True, verbose_name="Категории")

    author = models.ForeignKey(to=User, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Автор")

    cache_version = models.PositiveSmallIntegerField(default=0, verbose_name="Версия кэша")

    def set_total_rating(self):
        result = 0
        if self.pk:
            all_reviews = NewsReview.objects.filter(news=self)

            if all_reviews.exists():
                for item in all_reviews:
                    result += item.rating
                result /= all_reviews.count()
                result = round(result, 0)

            self.rating = result

    def set_popularity(self):
        if self.pk:
            result = 0
            result += NewsReview.objects.filter(news=self).count() * self.rating
            result += NewsComment.objects.filter(news=self).count() * 20
            self.popularity = int(result)

    def set_h2_headings(self):
        """Извлекает все заголовки H2 из контента статьи"""
        headings = []

        # Обрабатываем оба поля с контентом
        for field_name in ['content_start', 'content_end']:
            content = getattr(self, field_name)
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                for h2 in soup.find_all('h2'):
                    text = h2.get_text().strip()
                    if text:
                        # Создаем якорную ссылку (slug)
                        anchor = slugify(text)

                        h2['id'] = anchor
                        h2['class'] = h2.get('class', []) + ['anchor-heading']
                        headings.append({
                            'text': text,
                            'anchor': anchor
                        })
                setattr(self, field_name, str(soup))

        self.headings = headings

    def change_cache_version(self):
        if self.cache_version >= 100:
            self.cache_version = 0
        else:
            self.cache_version += 1

    @property
    def stars_on_count(self):
        return self.rating

    @property
    def stars_off_count(self):
        return 5 - self.rating

    @property
    def formated_published_date(self):
        return self.published_date.strftime('%d.%m.%y')

    class Meta:
        ordering = ["title"]
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = get_unique_slug(self, self.__class__, self.title)

        self.set_h2_headings()
        self.set_total_rating()
        self.set_popularity()
        self.change_cache_version()

        # Удаляем старое изображение при обновлении
        if self.pk:
            old_item = self.__class__.objects.get(pk=self.pk)
            if old_item.preview and old_item.preview != self.preview:
                old_item.preview.delete(save=False)

            if old_item.status != self.status:
                self.status_updated_at = now()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Удаляем файл изображения при удалении шага
        if self.preview:
            self.preview.delete(save=False)
        super().delete(*args, **kwargs)

class NewsReview(models.Model):
    news = models.ForeignKey(to=News, on_delete=models.CASCADE, verbose_name="Статья")
    author = models.ForeignKey(to=User, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Автор")
    rating = models.PositiveSmallIntegerField(default=0,
                                              validators=[
                                                  MaxValueValidator(5),
                                                  MinValueValidator(1)
                                              ], verbose_name="Рейтинг")

    class Meta:
        verbose_name = "Оценка статьи"
        verbose_name_plural = "Оценки статей"

    def __str__(self):
        return f"От {self.author} для '{self.news}'"

class NewsComment(models.Model):
    text = models.TextField(default="", max_length=1024, verbose_name="Текст")
    image = models.ImageField(upload_to=news_comments_image_path, blank=True, null=True, verbose_name="Изображение")
    optimized_image_small = ImageSpecField(
        source='image',
        processors=[ResizeToFill(256, 170)],  # Размер оптимизированного изображения
        format='WebP',
        options={'quality': 100}
    )
    news = models.ForeignKey(to=News, on_delete=models.CASCADE, verbose_name="Статья")
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    published_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    likes = models.PositiveSmallIntegerField(default=0, verbose_name="Кол-во лайков")
    dislikes = models.PositiveSmallIntegerField(default=0, verbose_name="Кол-во дизлайков")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                               verbose_name="Ответный комментарий")

    def __str__(self):
        return f"От {self.author} для '{self.news}'"

    class Meta:
        ordering = ['author']
        verbose_name = "Комментарий к статье"
        verbose_name_plural = "Комментарии к статьям"

    def save(self, *args, **kwargs):
        # Удаляем старое изображение при обновлении
        if self.pk:
            old_item = self.__class__.objects.get(pk=self.pk)
            if old_item.image and old_item.image != self.image:
                old_item.image.delete(save=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Удаляем файл изображения при удалении шага
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)
