import os
from uuid import uuid4

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.utils.timezone import now, timedelta
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from additions.views import Status, Visibility, get_unique_slug, add_watermark
from categories.models import RecipeCategory
from users.models import User


class Difficulty:
    NEWBIE = 1
    NORMAL = 2
    EXPERIENCE = 3
    ADVANCED = 4
    PROFESSIONAL = 5

    List = (
        (NEWBIE, "Новичок"),
        (NORMAL, "Нормально"),
        (EXPERIENCE, "Требует опыта"),
        (ADVANCED, "Для продвинутых"),
        (PROFESSIONAL, "Профессионал"),
    )

class Scipy:
    NEWBIE = 1
    NORMAL = 2
    EXPERIENCE = 3
    ADVANCED = 4
    PROFESSIONAL = 5

    List = (
        (NEWBIE, "Без остроты"),
        (NORMAL, "Слабая острота"),
        (EXPERIENCE, "Умеренно остро"),
        (ADVANCED, "Достаточно остро"),
        (PROFESSIONAL, "Очень остро!"),
    )

class Units:
    List = (
        ("г", "Граммы"),
        ("кг", "Килограммы"),
        ("л", "Литры"),
        ("мл", "Миллилитры"),
        ("ст", "Стаканы"),
        ("ст.л.", "Столовые ложки"),
        ("ч.л.", "Чайные ложки"),
        ("шт", "Штуки"),
        ("щеп", "Щепотки"),
    )

def recipe_step_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"image_{uuid4().hex}.{ext}"
    return os.path.join("recipe_step_images", filename)

def ingredient_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"image_{uuid4().hex}.{ext}"
    return os.path.join("ingredient_icons", filename)

def recipe_preview_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"image_{uuid4().hex}.{ext}"
    return os.path.join("recipe_previews", filename)

def recipe_comments_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"image_{uuid4().hex}.{ext}"
    return os.path.join("recipe_comments_images", filename)

class Ingredient(models.Model):
    title = models.CharField(max_length=64, verbose_name="Название")
    slug = models.SlugField(blank=True, default=slugify(title), verbose_name="Ссылочное название")
    icon = models.FileField(upload_to=ingredient_image_path, blank=True, null=True, verbose_name="Иконка")
    calory_count = models.PositiveSmallIntegerField(default=0, verbose_name="Кол-во калорий")
    weight_per_unit = models.PositiveSmallIntegerField(default=0, verbose_name="Вес 1 штуки")
    popularity = models.PositiveSmallIntegerField(default=0, verbose_name="Популярность")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def save(self, *args, **kwargs):
        self.slug = get_unique_slug(self, self.__class__, self.title)
        # Удаляем старое изображение при обновлении
        if self.pk:
            old_item = self.__class__.objects.get(pk=self.pk)
            if old_item.icon and old_item.icon != self.icon:
                old_item.icon.delete(save=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Удаляем файл изображения при удалении шага
        if self.icon:
            self.icon.delete(save=False)
        super().delete(*args, **kwargs)

class RecipePreview(models.Model):
    preview_1 = models.ImageField(upload_to=recipe_preview_image_path, verbose_name="Превью 1")
    preview_2 = models.ImageField(upload_to=recipe_preview_image_path, blank=True, null=True, verbose_name="Превью 2")
    preview_3 = models.ImageField(upload_to=recipe_preview_image_path, blank=True, null=True, verbose_name="Превью 3")

    optimized_image_1_small = ImageSpecField(
        source='preview_1',
        processors=[ResizeToFill(525, 350)],  # Размер оптимизированного изображения
        format='WebP',
        options={'quality': 100}
    )
    optimized_image_1 = ImageSpecField(
        source='preview_1',
        processors=[ResizeToFill(1536, 1024)],  # Размер оптимизированного изображения
        format='WebP',
        options={'quality': 85}
    )
    optimized_image_2 = ImageSpecField(
        source='preview_2',
        processors=[ResizeToFill(1536, 1024)],  # Размер оптимизированного изображения
        format='WebP',
        options={'quality': 85}
    )
    optimized_image_3 = ImageSpecField(
        source='preview_3',
        processors=[ResizeToFill(1536, 1024)],  # Размер оптимизированного изображения
        format='WebP',
        options={'quality': 85}
    )

    class Meta:
        verbose_name = "Превью в рецепте"
        verbose_name_plural = "Превью в рецептах"

    def save(self, *args, **kwargs):
        # Удаляем старое изображение при обновлении
        if self.pk:
            old_item = self.__class__.objects.get(pk=self.pk)
            if old_item.preview_1 and old_item.preview_1 != self.preview_1:
                old_item.preview_1.delete(save=False)
            if old_item.preview_2 and old_item.preview_2 != self.preview_2:
                old_item.preview_2.delete(save=False)
            if old_item.preview_3 and old_item.preview_3 != self.preview_3:
                old_item.preview_3.delete(save=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Удаляем файл изображения при удалении шага
        if self.preview_1:
            self.preview_1.delete(save=False)
        if self.preview_2:
            self.preview_2.delete(save=False)
        if self.preview_3:
            self.preview_3.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.preview_1}"

class Recipe(models.Model):
    title = models.CharField(max_length=128, verbose_name="Название")
    slug = models.SlugField(blank=True, default=slugify(title), verbose_name="Ссылочное название")
    previews = models.ForeignKey(to=RecipePreview, on_delete=models.PROTECT, verbose_name="Превью")
    description_inner = models.TextField(max_length=1024, null=True, verbose_name="Описание внутри")
    description_card = models.CharField(max_length=64, null=True, verbose_name="Описание для карточки")

    video_url_first = models.URLField(blank=True, null=True, verbose_name="Основная ссылка на видео")
    video_url_second = models.URLField(blank=True, null=True, verbose_name="Запасная ссылка на видео")

    cook_time_full = models.DurationField(default=timedelta(0), verbose_name="Полное время приготовления")
    cook_time_active = models.DurationField(default=timedelta(0), verbose_name="Активное время приготовления")

    portions = models.PositiveSmallIntegerField(default=0, verbose_name="Порции")
    rating = models.PositiveSmallIntegerField(default=0,
        validators=[
            MaxValueValidator(5),
            MinValueValidator(0)
        ], verbose_name="Рейтинг")
    published_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    scipy = models.PositiveSmallIntegerField(choices=Scipy.List, verbose_name="Острота")
    difficulty = models.PositiveSmallIntegerField(choices=Difficulty.List, verbose_name="Сложность")
    popularity = models.PositiveSmallIntegerField(default=0, verbose_name="Популярность")

    status = models.PositiveSmallIntegerField(choices=Status.List, verbose_name="Статус")
    status_updated_at = models.DateTimeField(default=now, verbose_name="Время обновления статуса")
    visibility = models.PositiveSmallIntegerField(choices=Visibility.List, verbose_name="Видимость")

    categories = models.ManyToManyField(to=RecipeCategory, blank=True, verbose_name="Категории")

    author = models.ForeignKey(to=User, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Автор")

    cache_version = models.PositiveSmallIntegerField(default=0, verbose_name="Версия кэша")

    @property
    def stars_on_count(self):
        return self.rating

    @property
    def stars_off_count(self):
        return 5 - self.rating

    def calculate_total_calories(self):
        total_calories = 0
        for recipe_ingredient in self.recipeingredient_set.all():
            if recipe_ingredient.unit == 'г' or recipe_ingredient.unit == 'мл':
                calories_per_unit = recipe_ingredient.ingredient.calory_count / 100
                total_calories += float(recipe_ingredient.quantity) * calories_per_unit
            elif recipe_ingredient.unit == 'шт':
                total_calories += float(recipe_ingredient.quantity) * recipe_ingredient.ingredient.calory_count
        return int(total_calories)

    def set_total_rating(self):
        result = 0
        if self.pk:
            all_reviews = RecipeReview.objects.filter(recipe=self)

            if all_reviews.exists():
                for item in all_reviews:
                    result += item.rating
                result /= all_reviews.count()
                result = round(result, 0)

            self.rating = result

    def calculate_calories_per_100g(self):
        total_calories = 0  # Общая калорийность
        total_weight = 0  # Общий вес блюда в граммах

        recipe_ingredients = self.recipeingredient_set.all()

        for recipe_ingredient in recipe_ingredients:
            ingredient = recipe_ingredient.ingredient
            quantity = float(recipe_ingredient.quantity)
            unit = recipe_ingredient.unit

            # Переводим количество в граммы
            if unit == 'г':
                weight = quantity
            elif unit == 'кг':
                weight = quantity * 1000
            elif unit == 'мл':
                weight = quantity
            elif unit == 'л':
                weight = quantity * 1000
            elif unit == 'ст':
                weight = quantity * 250
            elif unit == 'ст.л.':
                weight = quantity * 15
            elif unit == 'ч.л.':
                weight = quantity * 5
            elif unit == 'шт':
                weight = quantity * ingredient.weight_per_unit  # Вес одной штуки
            else:
                weight = 0

            # Рассчитываем калорийность для текущего ингредиента
            ingredient_calories = (ingredient.calory_count / 100) * weight if weight != 0 else ingredient.calory_count * quantity
            total_calories += ingredient_calories
            total_weight += weight

        # Рассчитываем калорийность на 100 грамм
        if total_weight == 0:
            return 0  # Чтобы избежать деления на ноль

        calories_per_100g = int((total_calories / total_weight) * 100)
        return calories_per_100g

    def set_popularity(self):
        result = 0
        if self.pk:
            result += RecipeReview.objects.filter(recipe=self).count() * self.rating
            result += RecipeComment.objects.filter(recipe=self).count() * 20
            self.popularity = int(result)

    def change_cache_version(self):
        if self.pk:
            if self.cache_version >= 100:
                self.cache_version = 0
            else:
                self.cache_version += 1

    class Meta:
        ordering = ["title"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = get_unique_slug(self, self.__class__, self.title)
        self.set_total_rating()
        self.set_popularity()
        self.change_cache_version()
        if self.pk:
            old_status = get_object_or_404(self.__class__, pk=self.pk).status
            if old_status != self.status:
                self.status_updated_at = now()
        super().save(*args, **kwargs)

class RecipeStep(models.Model):
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE, verbose_name="Рецепт")
    image = models.ImageField(upload_to=recipe_step_image_path, verbose_name="Изображение")
    image_watermark = models.ImageField(upload_to=recipe_step_image_path, blank=True, null=True, verbose_name="Изображение с водяным знаком")
    text = models.TextField(max_length=512, verbose_name="Текст")
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name="Позиция")

    optimized_image = ImageSpecField(
        source='image',
        processors=[ResizeToFill(1536, 1024)],  # Размер оптимизированного изображения
        format='WebP',
        options={'quality': 85}
    )
    optimized_image_watermark = ImageSpecField(
        source='image_watermark',
        processors=[ResizeToFill(1536, 1024)],  # Размер оптимизированного изображения
        format='WebP',
        options={'quality': 85}
    )

    class Meta:
        verbose_name = "Шаг в рецепте"
        verbose_name_plural = "Шаги в рецептах"
        ordering = ["sort_order"]

    def save(self, *args, **kwargs):
        if self.pk:
            old_item = self.__class__.objects.get(pk=self.pk)
            added = False
            if self.image and not self.image_watermark:
                self.image_watermark = add_watermark(self.image)
                added = True
            if old_item.image and old_item.image != self.image:
                old_item.image.delete(save=False)
                if not added:
                    old_item.image_watermark.delete(save=False)
                    self.image_watermark = add_watermark(self.image)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Удаляем файл изображения при удалении шага
        if self.image:
            self.image.delete(save=False)
            self.image_watermark.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Для рецепта '{self.recipe}'"

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name="Рецепт")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент")
    quantity = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Количество")
    unit = models.CharField(choices=Units.List, max_length=64, verbose_name="Размерность")
    can_exclude = models.BooleanField(default=False, verbose_name="Можно убрать")

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.ingredient.title} для {self.recipe.title}"

class RecipeReview(models.Model):
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE, verbose_name="Рецепт")
    author = models.ForeignKey(to=User, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Автор")
    rating = models.PositiveSmallIntegerField(default=0,
                                              validators=[
                                                  MaxValueValidator(5),
                                                  MinValueValidator(1)
                                              ], verbose_name="Рейтинг")

    class Meta:
        verbose_name = "Оценка рецепта"
        verbose_name_plural = "Оценки рецептов"

    def __str__(self):
        return f"От {self.author} для '{self.recipe}'"

class RecipeComment(models.Model):
    text = models.TextField(default="", max_length=1024, verbose_name="Текст")
    image = models.ImageField(upload_to=recipe_comments_image_path, blank=True, null=True, verbose_name="Изображение")
    optimized_image_small = ImageSpecField(
        source='image',
        processors=[ResizeToFill(256, 170)],  # Размер оптимизированного изображения
        format='WebP',
        options={'quality': 100}
    )
    recipe = models.ForeignKey(to=Recipe, on_delete=models.CASCADE, verbose_name="Рецепт")
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    published_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    likes = models.PositiveSmallIntegerField(default=0, verbose_name="Кол-во лайков")
    dislikes = models.PositiveSmallIntegerField(default=0, verbose_name="Кол-во дизлайков")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                               verbose_name="Ответный комментарий")

    def __str__(self):
        return f"От {self.author} для '{self.recipe}'"

    class Meta:
        ordering = ['author']
        verbose_name = "Комментарий к рецепту"
        verbose_name_plural = "Комментарии к рецептам"
        
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
