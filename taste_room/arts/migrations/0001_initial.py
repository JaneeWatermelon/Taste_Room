# Generated by Django 5.1.6 on 2025-05-12 09:39

import arts.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Art',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=128, null=True, verbose_name='Название')),
                ('description', models.CharField(blank=True, max_length=256, null=True, verbose_name='Описание')),
                ('image', models.ImageField(upload_to=arts.models.art_image_path, verbose_name='Изображение')),
                ('url', models.URLField(verbose_name='Ссылка')),
            ],
            options={
                'verbose_name': 'Реклама',
                'verbose_name_plural': 'Рекламы',
            },
        ),
    ]
