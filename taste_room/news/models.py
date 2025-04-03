from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import JSONField
from django.utils.text import slugify

from bs4 import BeautifulSoup

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from recipes.models import Status, Visibility, transliterate_russian_to_pseudo_english, get_unique_slug
from users.models import User, Comment, Review
from categories.models import RecipeCategory

class News(models.Model):
    title = models.CharField(max_length=128, verbose_name="Название")
    slug = models.SlugField(blank=True, default=slugify(title), verbose_name="Ссылочное название")
    preview = models.ImageField(upload_to="news_previews/", verbose_name="Превью")
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
    headings = JSONField(default=list, blank=True, null=True, verbose_name="Содержание")

    rating = models.PositiveSmallIntegerField(default=0,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ], verbose_name="Рейтинг")
    published_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")

    status = models.PositiveSmallIntegerField(choices=Status.List, verbose_name="Статус")
    visibility = models.PositiveSmallIntegerField(choices=Visibility.List, verbose_name="Видимость")
    popularity = models.PositiveSmallIntegerField(default=0, verbose_name="Популярность")

    categories = models.ManyToManyField(to=RecipeCategory, blank=True, verbose_name="Категории")

    author = models.ForeignKey(to=User, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Автор")
    comments = models.ManyToManyField(to=Comment, blank=True, verbose_name="Комментарии")
    reviews = models.ManyToManyField(to=Review, blank=True, verbose_name="Оценки")

    def set_total_rating(self):
        result = 0
        all_reviews = self.reviews.all()
        if all_reviews.exists():
            for item in all_reviews:
                result += item.rating
            result /= all_reviews.count()
            result = round(result, 0)
        self.rating = result

    def set_popularity(self):
        result = 0
        result += self.reviews.all().count() * self.rating
        result += self.comments.all().count() * 20
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

    class Meta:
        ordering = ["title"]
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        old_slug = slugify(transliterate_russian_to_pseudo_english(self.title))
        self.slug = get_unique_slug(self, News, old_slug)

        self.set_h2_headings()

        self.set_total_rating()
        self.set_popularity()
        super().save(*args, **kwargs)
