from django.db import models

class Art(models.Model):
    title = models.CharField(max_length=128, blank=True, null=True, verbose_name="Название")
    description = models.CharField(max_length=256, blank=True, null=True, verbose_name="Описание")
    image = models.ImageField(upload_to="art_images/", verbose_name="Изображение")
    url = models.URLField(verbose_name="Ссылка")

    class Meta:
        verbose_name = "Реклама"
        verbose_name_plural = "Рекламы"

    def __str__(self):
        return f"{self.title} | {self.url}"
