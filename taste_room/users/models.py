import os
import random
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from additions.models import Socials


class AchivLevels:
    List = [
        (1, "Серебро"),
        (2, "Золото"),
        (3, "Рубин"),
    ]

class DisplayNames:
    List = [
        (1, "Вкусная печенька 🍪"),
        (2, "Карамельный латте ☕"),
        (3, "Забавный пирожок 🥟"),
        (4, "Сладкий кекс 🧁"),
        (5, "Ароматный багет 🥖"),
        (6, "Сочный бургер 🍔"),
        (7, "Хрустящий круассан 🥐"),
        (8, "Нежный чизкейк 🍰"),
        (9, "Пряный глинтвейн 🍷"),
        (10, "Фруктовый смузи 🍹"),
        (11, "Свежий салат 🥗"),
        (12, "Домашняя пицца 🍕"),
        (13, "Сытный рамен 🍜"),
        (14, "Мятный мохито 🍸"),
        (15, "Золотой блинчик 🥞"),

        (16, "Сливочный пудинг 🍮"),
        (17, "Острый чили 🌶️"),
        (18, "Арбузный щербет 🍉"),
        (19, "Медовый пряник 🍯"),
        (20, "Клубничный торт"),
        (21, "Копчёный бекон 🥓"),
        (22, "Ванильное мороженое 🍦"),
        (23, "Грибной супчик 🍄"),
        (24, "Шоколадный фондан 🍫"),
        (25, "Лимонный тарт 🍋"),
        (26, "Кокосовый макарун 🥥"),
        (27, "Ореховый брауни 🥜"),
        (28, "Тыквенный латте 🎃"),
        (29, "Малиновый джем 🍓"),
        (30, "Сырный фондю 🧀"),
    ]

    def get_random_display_name(self):
        return self.List[random.randint(0, len(self.List)-1)][1]

def achiv_icon_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"image_{uuid4().hex}.{ext}"
    return os.path.join("achiv_icons", filename)

def users_avatar_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"image_{uuid4().hex}.{ext}"
    return os.path.join("users_avatars", filename)

class CategoryAchievement(models.Model):
    title = models.CharField(max_length=64, verbose_name="Название")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Категория достижения"
        verbose_name_plural = "Категории достижений"

class GeneralAchievementCondition(models.Model):
    title = models.CharField(max_length=256, verbose_name="Общее условие")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Условие получения достижения"
        verbose_name_plural = "Условия получения достижений"

class Achievement(models.Model):
    title = models.CharField(default="", max_length=128, blank=True, null=True, verbose_name="Название")
    icon = models.FileField(upload_to=achiv_icon_image_path, verbose_name="Иконка")
    level = models.PositiveSmallIntegerField(choices=AchivLevels.List, verbose_name="Уровень")
    category = models.ForeignKey(to=CategoryAchievement, on_delete=models.CASCADE, verbose_name="Категория")
    condition_general = models.ForeignKey(to=GeneralAchievementCondition, on_delete=models.CASCADE, verbose_name="Общее условие")
    condition_self = models.CharField(max_length=128, verbose_name="Конкретное условие")

    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"

    def save(self, *args, **kwargs):
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

class Color(models.Model):
    title = models.CharField(default="", blank=True, null=True, max_length=64, verbose_name="Название")
    hash = models.CharField(max_length=64, verbose_name="Цвет фона")
    text_hash = models.CharField(default="#000000", max_length=64, verbose_name="Цвет текста")
    sort_order = models.PositiveSmallIntegerField(default=0, verbose_name="Поле сортировки")

    def __str__(self):
        return self.title if self.title else self.hash

    class Meta:
        verbose_name = "Цвет фона"
        verbose_name_plural = "Цвета фона"
        ordering = ['sort_order']

class User(AbstractUser):
    name = models.CharField(default=DisplayNames.List[0][1], blank=True, null=True, max_length=32, verbose_name="Отображаемое имя")
    avatar = models.ImageField(upload_to=users_avatar_image_path, blank=True, null=True, verbose_name="Аватарка")
    optimized_image = ImageSpecField(
        source='avatar',
        processors=[ResizeToFill(128, 128)],  # Размер оптимизированного изображения
        format='WebP',
        options={'quality': 100}
    )
    optimized_image_small = ImageSpecField(
        source='avatar',
        processors=[ResizeToFill(64, 64)],  # Размер оптимизированного изображения
        format='WebP',
        options={'quality': 100}
    )
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    background_color = models.ForeignKey(to=Color, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Цвет фона")

    description_profile = models.TextField(default="Добро пожаловать в мой профиль! Я увлечен(а) кулинарией и верю, "
                                                   "что вкусная еда делает жизнь ярче. Надеюсь, мои рецепты и "
                                                   "советы будут полезны для вас!",
                                           blank=True, null=True, max_length=512, verbose_name="Описание профиля")
    description_recipe = models.TextField(default="Привет! Я обожаю готовить и экспериментировать на кухне. "
                                                  "Для меня кулинария — это не просто процесс, а настоящее искусство. "
                                                  "Буду рад(а) делиться с вами своими любимыми рецептами и советами!",
                                          blank=True, null=True, max_length=512, verbose_name="Описание для рецепта")
    description_news = models.TextField(default="Добро пожаловать в мой кулинарный блог! "
                                                "Здесь я делюсь интересными фактами, советами и историями о еде. "
                                                "Надеюсь, мои статьи помогут вам открыть для себя что-то новое и "
                                                "вдохновят на эксперименты!",
                                        blank=True, null=True, max_length=512, verbose_name="Описание для статьи")

    socials = models.ForeignKey(to=Socials, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Соцсети")

    liked_recipes = models.ManyToManyField(to='recipes.Recipe', blank=True, verbose_name="Понравившиеся рецепты")

    liked_recipe_comments = models.ManyToManyField(to='recipes.RecipeComment', blank=True, related_name='liked_recipe_comments_set', verbose_name="Лайкнутые комментарии рецепта")
    disliked_recipe_comments = models.ManyToManyField(to='recipes.RecipeComment', blank=True, related_name='disliked_recipe_comments_set', verbose_name="Дизлайкнутые комментарии рецептов")

    liked_news_comments = models.ManyToManyField(to='news.NewsComment', blank=True, related_name='liked_news_comments_set', verbose_name="Лайкнутые комментарии статьи")
    disliked_news_comments = models.ManyToManyField(to='news.NewsComment', blank=True, related_name='disliked_news_comments_set', verbose_name="Дизлайкнутые комментарии статей")

    subscriptions = models.ManyToManyField(to='self', symmetrical=False, blank=True, related_name='subscribers', verbose_name="Подписки")

    choosed_achiv = models.ForeignKey(to=Achievement, blank=True, null=True, on_delete=models.SET_NULL, related_name="choosed_achiv_set", verbose_name="Выбранное достижение")
    achivs = models.ManyToManyField(to=Achievement, blank=True, related_name="achivs_set", verbose_name="Полученные достижения")

    @property
    def formated_date_joined(self):
        return self.date_joined.strftime('%d.%m.%Y')

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['username']
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def save(self, *args, **kwargs):
        # Удаляем старое изображение при обновлении
        if self.pk:
            old_item = self.__class__.objects.get(pk=self.pk)
            if old_item.avatar and old_item.avatar != self.avatar:
                old_item.avatar.delete(save=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Удаляем файл изображения при удалении шага
        if self.avatar:
            self.avatar.delete(save=False)
        super().delete(*args, **kwargs)
