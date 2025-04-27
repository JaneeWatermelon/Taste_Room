from django.db import models
from django.db.models import ManyToManyField
from django.utils.text import slugify

from additions.views import get_unique_slug


class RecipeCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(blank=True, default=slugify(name), verbose_name="Ссылочное название")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="Подкатегория")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def save(self, *args, **kwargs):
        self.slug = get_unique_slug(self, self.__class__, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class CategoryGroup(models.Model):
    title = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(blank=True, default=slugify(title), verbose_name="Ссылочное название")
    categories = ManyToManyField(to=RecipeCategory, blank=True, verbose_name="Категории")

    class Meta:
        verbose_name = "Группа категорий"
        verbose_name_plural = "Группы категорий"

    def save(self, *args, **kwargs):
        self.slug = get_unique_slug(self, self.__class__, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
