from django.db import models


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
