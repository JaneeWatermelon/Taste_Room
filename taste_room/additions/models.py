import uuid

from django.db import models
from django.utils.timezone import now, timedelta


class Socials(models.Model):
    telegram = models.URLField(blank=True, null=True, verbose_name="Телеграм")
    vk = models.URLField(blank=True, null=True, verbose_name="ВКонтакте")
    pinterest = models.URLField(blank=True, null=True, verbose_name="Pinterest")
    youtube = models.URLField(blank=True, null=True, verbose_name="Youtube")
    rutube = models.URLField(blank=True, null=True, verbose_name="Rutube")

    class Meta:
        verbose_name = "Соцсеть"
        verbose_name_plural = "Соцсети"

class MetaTag(models.Model):
    url = models.CharField(max_length=200, unique=True, verbose_name="URL страницы")
    title = models.CharField(max_length=200, verbose_name="Заголовок (title)")
    description = models.TextField(verbose_name="Описание (description)")
    og_title = models.CharField(max_length=200, blank=True, verbose_name="OpenGraph Title")
    og_description = models.TextField(blank=True, verbose_name="OpenGraph Description")
    og_image = models.ImageField(upload_to="meta_og_images/", verbose_name="OpenGraph Image URL")

    class Meta:
        verbose_name = "Мета-тег"
        verbose_name_plural = "Мета-теги"

    def __str__(self):
        return f"Мета-теги для {self.url}"

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
