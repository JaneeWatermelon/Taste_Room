from django.conf import settings
from django.contrib.staticfiles import finders
from django.db.models import Q
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.views.generic import TemplateView


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

    TypeAndDescr = {
        ALL: ["Все", "виден всем и везде"],
        PROFILE: ["Только в профиле", "виден всем у вас на странице"],
        SUBS: ["Только подписчики", "виден только подписчикам"],
        ME: ["Только я", "приватный, виден только вам"],
    }

class YandexWebMasterView(TemplateView):
    template_name = "additions/yandex_7de2f9bee8148ab5.html"

class RobotsView(TemplateView):
    template_name = "additions/robots.txt"

class Error404View(TemplateView):
    template_name = "additions/error_404.html"

class ErrorModeratorView(TemplateView):
    template_name = "additions/error_moderator.html"
        

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
    transliterated_text = ''.join(transliteration_table.get(char, char) for char in text.lower())
    return transliterated_text

def get_unique_slug(instance, model_class, slug_field):
    old_slug = slugify(transliterate_russian_to_pseudo_english(slug_field))
    new_slug = old_slug
    all_slug_models = model_class.objects.filter(slug=new_slug)
    if all_slug_models.exists() and all_slug_models.first().id != instance.id:
        new_slug = f"{old_slug}-{instance.id}"
    return new_slug

def get_recipes_related(queryset):
    return queryset.select_related("previews", "author").prefetch_related(
            "recipereview_set",
            "recipeingredient_set",
            "recipeingredient_set__ingredient",
        )

def get_recipes_PUBLISHED_ALL_SUBS(user, ready_queryset=None):
    from recipes.models import Recipe
    model_class = Recipe
    if user.is_authenticated:
        subscribed_ids = user.subscriptions.values_list('id', flat=True)
        if ready_queryset:
            queryset = ready_queryset.filter(
                Q(visibility=Visibility.ALL, status=Status.PUBLISHED) |
                Q(visibility=Visibility.SUBS, author_id__in=subscribed_ids, status=Status.PUBLISHED)
            ).distinct()
        else:
            queryset = model_class.objects.filter(
                Q(visibility=Visibility.ALL, status=Status.PUBLISHED) |
                Q(visibility=Visibility.SUBS, author_id__in=subscribed_ids, status=Status.PUBLISHED)
            ).distinct()
    else:
        if ready_queryset:
            queryset = ready_queryset.filter(
                Q(visibility=Visibility.ALL, status=Status.PUBLISHED)
            ).distinct()
        else:
            queryset = model_class.objects.filter(
                Q(visibility=Visibility.ALL, status=Status.PUBLISHED)
            ).distinct()

    return queryset.select_related("previews", "author").prefetch_related(
            "recipereview_set",
            "recipeingredient_set",
            "recipeingredient_set__ingredient",
        )

def get_recs_recipes(user, recipe_categories, exclude_pk, count):
    from recipes.models import Recipe
    model_class = Recipe
    if user.is_authenticated:
        subscribed_ids = user.subscriptions.values_list('id', flat=True)
        queryset = list(model_class.objects.filter(
            Q(visibility=Visibility.ALL, status=Status.PUBLISHED, categories__in=recipe_categories) |
            Q(visibility=Visibility.SUBS, author_id__in=subscribed_ids, status=Status.PUBLISHED,
              categories__in=recipe_categories)
        ).distinct().exclude(pk=exclude_pk)[:count].select_related("previews", "author").prefetch_related(
            "recipereview_set",
            "recipeingredient_set",
            "recipeingredient_set__ingredient"
        ))
        if len(queryset) < count:
            additional_items = list(model_class.objects.filter(
                Q(visibility=Visibility.ALL, status=Status.PUBLISHED) |
                Q(visibility=Visibility.SUBS, author_id__in=subscribed_ids, status=Status.PUBLISHED)
            ).distinct().exclude(pk=exclude_pk, categories__in=recipe_categories)[:count-len(queryset)].select_related("previews", "author").prefetch_related(
                "recipereview_set",
                "recipeingredient_set",
                "recipeingredient_set__ingredient"
            ))
            queryset += additional_items
        if len(queryset) < 4:
            queryset = None
    else:
        queryset = list(model_class.objects.filter(
            Q(visibility=Visibility.ALL, status=Status.PUBLISHED, categories__in=recipe_categories)
        ).distinct().exclude(pk=exclude_pk)[:10])
        if len(queryset) < 10:
            additional_items = list(model_class.objects.filter(
                Q(visibility=Visibility.ALL, status=Status.PUBLISHED)
            ).distinct().exclude(pk=exclude_pk, categories__in=recipe_categories)[:10-len(queryset)].select_related("previews", "author").prefetch_related(
                "recipereview_set",
                "recipeingredient_set",
                "recipeingredient_set__ingredient"
            ))
            queryset += additional_items
        if len(queryset) < 4:
            queryset = None

    return queryset


def get_news_PUBLISHED_ALL_SUBS(user):
    from news.models import News
    model_class = News
    if user.is_authenticated:
        queryset = model_class.objects.filter(
            Q(visibility=Visibility.ALL, status=Status.PUBLISHED) |
            Q(visibility=Visibility.SUBS, author__subscribers=user, status=Status.PUBLISHED)
        ).distinct()
    else:
        queryset = model_class.objects.filter(
            Q(visibility=Visibility.ALL, status=Status.PUBLISHED)
        ).distinct()

    return queryset.select_related("author").prefetch_related(
            "newsreview_set",
        )


from django.db.models import Q
from news.models import News


def get_recs_news(user, categories, exclude_pk, count):
    base_filters = Q(status=Status.PUBLISHED) & ~Q(pk=exclude_pk)
    visibility_filters = Q(visibility=Visibility.ALL)

    if user.is_authenticated:
        subscribed_ids = user.subscriptions.values_list('id', flat=True)
        visibility_filters |= Q(visibility=Visibility.SUBS, author_id__in=subscribed_ids)

    # Основной запрос с приоритетными категориями
    queryset = News.objects.filter(
        base_filters &
        visibility_filters &
        Q(categories__in=categories)
    ).distinct().select_related("author").prefetch_related("newsreview_set")[:count]

    queryset = list(queryset)

    # Дополняем записями из других категорий если нужно
    if len(queryset) < count:
        additional = News.objects.filter(
            base_filters &
            visibility_filters &
            ~Q(categories__in=categories)
        ).distinct().select_related("author").prefetch_related("newsreview_set")[:count - len(queryset)]
        queryset += list(additional)

    return queryset if len(queryset) >= 4 else None

def get_news_comments(news_object):
    from news.models import NewsComment
    model_class = NewsComment
    queryset = model_class.objects.filter(news=news_object, parent=None)

    return queryset.select_related("author", "parent").order_by('-published_date')


def get_recipes_author_page(user, author):
    from recipes.models import Recipe
    model_class = Recipe
    if user.is_authenticated:
        subscribed_ids = user.subscriptions.values_list('id', flat=True)
        queryset = model_class.objects.filter(
            Q(visibility__in=[Visibility.ALL, Visibility.PROFILE], author=author, status=Status.PUBLISHED) |
            Q(visibility=Visibility.SUBS, author_id__in=subscribed_ids, author=author, status=Status.PUBLISHED)
        ).distinct()
    else:
        queryset = model_class.objects.filter(
            Q(visibility__in=[Visibility.ALL, Visibility.PROFILE], author=author, status=Status.PUBLISHED)
        ).distinct()

    return queryset.select_related("previews", "author").prefetch_related(
            "recipereview_set",
            "recipeingredient_set",
            "recipeingredient_set__ingredient"
        )

def get_news_author_page(user, author):
    from news.models import News
    model_class = News
    if user.is_authenticated:
        queryset = model_class.objects.filter(
            Q(visibility__in=[Visibility.ALL, Visibility.PROFILE], author=author, status=Status.PUBLISHED) |
            Q(visibility=Visibility.SUBS, author__subscribers=user, author=author, status=Status.PUBLISHED)
        ).distinct()
    else:
        queryset = model_class.objects.filter(
            Q(visibility__in=[Visibility.ALL, Visibility.PROFILE], author=author, status=Status.PUBLISHED)
        ).distinct()

    return queryset.select_related("author").prefetch_related(
            "newsreview_set",
        )


def _prepare_empty_block():
    html = render_to_string('additions/empty_block.html')

    return {
        'html': html,
        'answer': "Данные успешно обновлены",
    }

def set_meta_tags(request, title, description, og_title=None, og_description=None, image=None,):
    if image:
        request.meta_og_image = image
    request.meta_title = title
    request.meta_description = description
    if og_title:
        request.meta_og_title = og_title
    else:
        request.meta_og_title = title

    if og_description:
        request.meta_og_description = og_description
    else:
        request.meta_og_description = description


from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO
from django.core.files import File


def add_watermark(image_field, watermark_text="tasteroom.ru"):
    """Добавляет водяной знак на изображение"""


    def text_sizes(text_message, fontsize=28, img_width=100):
        # Create a blank canvas
        canvas = Image.new('RGB', (img_width, 100))

        # Get a drawing context
        text_draw = ImageDraw.Draw(canvas)
        text_font = ImageFont.load_default(fontsize)

        white = (255, 255, 255)
        text_draw.text((10, 10), text_message, font=text_font, fill=white)

        # Find bounding box
        bbox = canvas.getbbox()
        return int(bbox[2]-bbox[0]), int(bbox[3]-bbox[1])

    # Открываем оригинальное изображение
    img = Image.open(image_field)

    # Создаем прозрачный слой для водяного знака
    watermark = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(watermark)

    font_size = int(img.width / 20)
    font = ImageFont.load_default(font_size)

    # Позиционирование текста (по центру)
    text_width, text_height = text_sizes(watermark_text, font_size, img.width)
    x = (img.width - text_width) / 2
    y = (img.height - text_height) / 2

    # Добавляем текст с прозрачностью
    draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, 32))

    # Совмещаем изображения
    watermarked = Image.alpha_composite(img.convert("RGBA"), watermark)

    # Конвертируем обратно в RGB (если исходное было JPG)
    if img.format == 'JPEG':
        watermarked = watermarked.convert("RGB")

    # Сохраняем в память
    buffer = BytesIO()
    watermarked.save(buffer, format=img.format)

    # Создаем Django File объект
    return File(buffer, name=image_field.name)