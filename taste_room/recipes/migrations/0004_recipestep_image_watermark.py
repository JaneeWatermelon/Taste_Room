# Generated by Django 5.1.6 on 2025-05-23 16:06

import recipes.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_ingredient_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipestep',
            name='image_watermark',
            field=models.ImageField(blank=True, null=True, upload_to=recipes.models.recipe_step_image_path, verbose_name='Изображение с водяным знаком'),
        ),
    ]
