import os
import uuid

from django.db import models
from django.utils.timezone import now, timedelta

from additions.validators import (validate_telegram_url, validate_vk_url, validate_pinterest_url,
                                  validate_youtube_url, validate_rutube_url)


def meta_og_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"image_{uuid.uuid4().hex}.{ext}"
    return os.path.join("meta_og_images", filename)

class Socials(models.Model):
    telegram = models.URLField(blank=True, null=True, verbose_name="Телеграм", validators=[validate_telegram_url])
    vk = models.URLField(blank=True, null=True, verbose_name="ВКонтакте", validators=[validate_vk_url])
    pinterest = models.URLField(blank=True, null=True, verbose_name="Pinterest", validators=[validate_pinterest_url])
    youtube = models.URLField(blank=True, null=True, verbose_name="Youtube", validators=[validate_youtube_url])
    rutube = models.URLField(blank=True, null=True, verbose_name="Rutube", validators=[validate_rutube_url])

    class Meta:
        verbose_name = "Соцсеть"
        verbose_name_plural = "Соцсети"

class MetaTag(models.Model):
    display_name = models.CharField(max_length=200, default="Страница", verbose_name="Название для админки")
    url = models.CharField(max_length=200, unique=True, verbose_name="URL страницы")
    title = models.CharField(max_length=200, verbose_name="Заголовок (title)")
    description = models.TextField(verbose_name="Описание (description)")
    og_title = models.CharField(max_length=200, blank=True, verbose_name="OpenGraph Title")
    og_description = models.TextField(blank=True, verbose_name="OpenGraph Description")
    og_image = models.ImageField(upload_to=meta_og_image_path, blank=True, null=True, verbose_name="OpenGraph Image URL")

    class Meta:
        verbose_name = "Мета-тег"
        verbose_name_plural = "Мета-теги"

    def __str__(self):
        return f"Мета-теги для {self.url}"

    def save(self, *args, **kwargs):
        # Удаляем старое изображение при обновлении
        if self.pk:
            old_item = self.__class__.objects.get(pk=self.pk)
            if old_item.og_image and old_item.og_image != self.og_image:
                old_item.og_image.delete(save=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Удаляем файл изображения при удалении шага
        if self.og_image:
            self.og_image.delete(save=False)
        super().delete(*args, **kwargs)

def default_expiration():
    return now() + timedelta(hours=24)

class EmailCode(models.Model):
    email = models.EmailField(verbose_name="Адрес электронной почты")
    code = models.UUIDField(default=uuid.uuid4, verbose_name="Код подтверждения")
    expiration = models.DateTimeField(default=default_expiration, verbose_name="Срок действия")
    accepted = models.BooleanField(default=False, verbose_name="Код подтверждён")

    class Meta:
        verbose_name = "Код подтверждения"
        verbose_name_plural = "Коды подтверждения"

    def __str__(self):
        return f"Код подтверждения {self.code} для {self.email} до {self.expiration}"

    def is_expired(self):
        return now() > self.expiration
