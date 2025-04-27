from django.shortcuts import render
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
