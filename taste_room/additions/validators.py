from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_telegram_url(value):
    if value and not value.startswith(('https://t.me/', 'https://telegram.me/')):
        raise ValidationError(
            _('Ссылка на Telegram должна начинаться с https://t.me/ или https://telegram.me/')
        )

def validate_vk_url(value):
    if value and not value.startswith(('https://vk.com/', 'https://m.vk.com/')):
        raise ValidationError(
            _('Ссылка на VK должна начинаться с https://vk.com/ или https://m.vk.com/')
        )

def validate_pinterest_url(value):
    if value and not value.startswith(('https://pinterest.com/', 'https://www.pinterest.com/')):
        raise ValidationError(
            _('Ссылка на Pinterest должна начинаться с https://pinterest.com/ или https://www.pinterest.com/')
        )

def validate_youtube_url(value):
    if value and not value.startswith(('https://youtube.com/', 'https://www.youtube.com/')):
        raise ValidationError(
            _('Ссылка на YouTube должна начинаться с https://youtube.com/ или https://www.youtube.com/')
        )

def validate_rutube_url(value):
    if value and not value.startswith(('https://rutube.ru/', 'https://www.rutube.ru/')):
        raise ValidationError(
            _('Ссылка на Rutube должна начинаться с https://rutube.ru/ или https://www.rutube.ru/')
        )