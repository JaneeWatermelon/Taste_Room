import os
from uuid import uuid4

from django.db import models


def art_image_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"image_{uuid4().hex}.{ext}"
    return os.path.join("art_images", filename)

class Art(models.Model):
    title = models.CharField(max_length=128, blank=True, null=True, verbose_name="Название")
    description = models.CharField(max_length=256, blank=True, null=True, verbose_name="Описание")
    image = models.ImageField(upload_to=art_image_path, verbose_name="Изображение")
    url = models.URLField(verbose_name="Ссылка")

    class Meta:
        verbose_name = "Реклама"
        verbose_name_plural = "Рекламы"

    def __str__(self):
        return f"{self.title} | {self.url}"

    def save(self, *args, **kwargs):
        # Удаляем старое изображение при обновлении
        if self.pk:
            old_item = self.__class__.objects.get(pk=self.pk)
            if old_item.image and old_item.image != self.image:
                old_item.image.delete(save=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Удаляем файл изображения при удалении шага
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)
