import math

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.template.defaulttags import comment
from django.utils.text import slugify
from django.utils.timezone import timedelta, now

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from users.models import User, Comment, Review
from categories.models import RecipeCategory

def transliterate_russian_to_pseudo_english(text):
    transliteration_table = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g',
        'д': 'd', 'е': 'e', 'ё': 'yo', 'ж': 'zh',
        'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k',
        'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
        'п': 'p', 'р': 'r', 'с': 's', 'т': 't',
        'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts',
        'ч': 'ch', 'ш': 'sh', 'щ': 'shch', 'ъ': '',
        'ь': '', 'э': 'e', 'ы': 'y', 'ю': 'yu', 'я': 'ya',
    }

    # Заменяем каждую букву на соответствующую
    transliterated_text = ''.join(transliteration_table.get(char.lower(), char.lower()) for char in text)
    return transliterated_text

def get_unique_slug(instance, model_class, old_slug):
    new_slug = old_slug
    all_slug_models = model_class.objects.filter(slug=new_slug)
    if all_slug_models.exists() and all_slug_models.first().id != instance.id:
        new_slug = f"{old_slug}-{instance.id}"
    return new_slug

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

class Status:
    PUBLISHED = 1
    UNPUBLISHED = 2
    DRAFT = 3
    MODERATION = 4

    List = (
        (PUBLISHED, "Опубликовано"),
        (UNPUBLISHED, "Не опубликовано"),
        (DRAFT, "Черновик"),
        (MODERATION, "На проверке"),
    )

class Visibility:
    ALL = 1
    PROFILE = 2
    SUBS = 3
    ME = 4

    List = (
        (ALL, "Все"),
        (PROFILE, "Только в профиле"),
        (SUBS, "Только подписчики"),
        (ME, "Только я"),
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

class Ingredient(models.Model):
    title = models.CharField(max_length=64, verbose_name="Название")
    slug = models.SlugField(blank=True, default=slugify(title), verbose_name="Ссылочное название")
    icon = models.FileField(upload_to="ingredient_icons/", verbose_name="Иконка")
    calory_count = models.PositiveSmallIntegerField(default=0, verbose_name="Кол-во калорий")
    weight_per_unit = models.PositiveSmallIntegerField(default=0, verbose_name="Вес 1 штуки")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def save(self, *args, **kwargs):
        old_slug = slugify(transliterate_russian_to_pseudo_english(self.title))
        self.slug = get_unique_slug(self, Ingredient, old_slug)
        super().save(*args, **kwargs)

class RecipeStep(models.Model):
    image = models.ImageField(upload_to="recipe_step_images/", verbose_name="Изображение")
    text = models.TextField(max_length=512, verbose_name="Текст")

    optimized_image = ImageSpecField(
        source='image',
        processors=[ResizeToFill(1536, 1024)],  # Размер оптимизированного изображения
        format='WebP',
        options={'quality': 85}
    )

    class Meta:
        verbose_name = "Шаг в рецепте"
        verbose_name_plural = "Шаги в рецептах"

    def __str__(self):
        return self.image.url

class RecipePreview(models.Model):
    preview_1 = models.ImageField(upload_to="recipe_previews/", verbose_name="Превью 1")
    preview_2 = models.ImageField(upload_to="recipe_previews/", blank=True, null=True, verbose_name="Превью 2")
    preview_3 = models.ImageField(upload_to="recipe_previews/", blank=True, null=True, verbose_name="Превью 3")

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

    def __str__(self):
        return f"{self.preview_1}"

class Recipe(models.Model):
    title = models.CharField(max_length=128, verbose_name="Название")
    slug = models.SlugField(blank=True, default=slugify(title), verbose_name="Ссылочное название")
    previews = models.ForeignKey(to=RecipePreview, on_delete=models.CASCADE, verbose_name="Превью")
    description_inner = models.TextField(max_length=1024, verbose_name="Описание внутри")
    description_card = models.CharField(max_length=64, verbose_name="Описание для карточки")

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
    visibility = models.PositiveSmallIntegerField(choices=Visibility.List, verbose_name="Видимость")

    categories = models.ManyToManyField(to=RecipeCategory, blank=True, verbose_name="Категории")

    author = models.ForeignKey(to=User, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Автор")
    comments = models.ManyToManyField(to=Comment, blank=True, verbose_name="Комментарии")
    ingredients = models.ManyToManyField(to=Ingredient, through='RecipeIngredient', verbose_name="Ингредиенты")
    steps = models.ManyToManyField(to=RecipeStep, verbose_name="Шаги")
    reviews = models.ManyToManyField(to=Review, blank=True, verbose_name="Оценки")

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
        all_reviews = self.reviews.all()

        if all_reviews.exists():
            for item in all_reviews:
                result += item.rating
            result /= all_reviews.count()
            result = round(result, 0)

        self.rating = result

    def calculate_calories_per_100g(self):
        total_calories = 0  # Общая калорийность
        total_weight = 0  # Общий вес блюда в граммах

        for recipe_ingredient in self.recipeingredient_set.all():
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
        result += self.reviews.all().count() * self.rating
        result += self.comments.all().count() * 20
        self.popularity = int(result)

    class Meta:
        ordering = ["title"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        old_slug = slugify(transliterate_russian_to_pseudo_english(self.title))
        self.slug = get_unique_slug(self, Recipe, old_slug)
        self.set_total_rating()
        self.set_popularity()
        super().save(*args, **kwargs)

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name="Рецепт")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент")
    quantity = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Количество")
    unit = models.CharField(choices=Units.List, max_length=64, verbose_name="Размерность")

    class Meta:
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецептах"

    def __str__(self):
        return f"{self.quantity} {self.unit} {self.ingredient.title} для {self.recipe.title}"
