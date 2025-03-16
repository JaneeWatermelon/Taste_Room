import random

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

from additions.models import Socials

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
    icon = models.FileField(upload_to="achiv_icons/", verbose_name="Иконка")
    level = models.PositiveSmallIntegerField(choices=AchivLevels.List, verbose_name="Уровень")
    category = models.ForeignKey(to=CategoryAchievement, on_delete=models.CASCADE, verbose_name="Категория")
    condition_general = models.ForeignKey(to=GeneralAchievementCondition, on_delete=models.CASCADE, verbose_name="Общее условие")
    condition_self = models.CharField(max_length=128, verbose_name="Конкретное условие")

    class Meta:
        verbose_name = "Достижение"
        verbose_name_plural = "Достижения"

class User(AbstractUser):
    name = models.CharField(default=DisplayNames.List[random.randint(0, 29)][1], blank=True, null=True, max_length=32, verbose_name="Отображаемое имя")
    avatar = models.ImageField(upload_to='users_avatars/', blank=True, null=True, verbose_name="Аватарка")
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    background_color = models.CharField(default="", max_length=64, blank=True, null=True, verbose_name="Цвет фона")

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

    liked_recipes_id = models.JSONField(default=list, blank=True, null=True, verbose_name="Понравившиеся рецепты")
    liked_comments_id = models.JSONField(default=list, blank=True, null=True, verbose_name="Лайкнутые комментарии")
    disliked_comments_id = models.JSONField(default=list, blank=True, null=True, verbose_name="Дизлайкнутые комментарии")
    subscribers_id = models.JSONField(default=list, blank=True, null=True, verbose_name="Подписчики")
    subscriptions_id = models.JSONField(default=list, blank=True, null=True, verbose_name="Подписки")

    choosed_achiv = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name="Выбранное достижение")
    achivs = models.ManyToManyField(to=Achievement, blank=True, verbose_name="Полученные достижения")

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['username']
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Comment(models.Model):
    text = models.TextField(default="", max_length=1024, verbose_name="Текст")
    image = models.ImageField(upload_to='comments_images/', blank=True, null=True, verbose_name="Изображение")
    author = models.ForeignKey(to=User, on_delete=models.CASCADE, verbose_name="Автор")
    published_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    likes = models.PositiveSmallIntegerField(default=0, verbose_name="Кол-во лайков")
    dislikes = models.PositiveSmallIntegerField(default=0, verbose_name="Кол-во дизлайков")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',
                               verbose_name="Ответный комментарий")

    def __str__(self):
        return f"Комментарий автора: {self.author}"

    class Meta:
        ordering = ['author']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

class Review(models.Model):
    author = models.ForeignKey(to=User, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Автор")
    rating = models.PositiveSmallIntegerField(default=0,
                                              validators=[
                                                  MaxValueValidator(5),
                                                  MinValueValidator(1)
                                              ], verbose_name="Рейтинг")

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"

    def __str__(self):
        return f"От {self.author}"
