import os

from django.conf import settings
from django.db.models.signals import post_delete, post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.urls import reverse

from additions.tasks import send_telegram_notification
from additions.views import Status, add_watermark
from recipes.models import (Recipe, RecipeComment, RecipeIngredient,
                            RecipeReview, RecipeStep)
from users.models import User


def change_units(instance):
    unit = instance.unit
    quantity = instance.quantity

    if unit == "г" and quantity >= 1000:
        instance.quantity /= 1000
        instance.unit = "кг"
    elif unit == "кг" and 0 < quantity < 1:
        instance.quantity *= 1000
        instance.unit = "г"
    elif unit == "л" and 0 < quantity < 1:
        instance.quantity *= 1000
        instance.unit = "мл"
    elif unit == "мл" and quantity >= 1000:
        instance.quantity /= 1000
        instance.unit = "л"

def send_telegram_message(instance):
    item_url = reverse("recipes:detail", kwargs={
        "pk": instance.id,
        "slug": instance.slug,
    })
    message = (
        f"<b>Новый рецепт!</b>\n\n"
        f"🍴 <b>Название:</b> {instance.title}\n"
        f"🍴 <b>Мини-описание:</b> {instance.description_card}\n"
        f"👨‍🍳 Автор: {instance.author.username}\n\n"
        f"🔗 Ссылка: {settings.DOMAIN_NAME}{item_url}\n"
        f"🔗 Ссылка на админку: {settings.DOMAIN_NAME}/admin/recipes/recipe/{instance.id}/change/"
    )
    send_telegram_notification.delay(message)

@receiver(pre_save, sender=Recipe)
def pre_save_recipe(sender, instance, **kwargs):
    if instance.pk:
        old_status = get_object_or_404(Recipe, id=instance.id).status
        new_status = instance.status
        if int(new_status) == Status.MODERATION and int(old_status) != Status.MODERATION:
            send_telegram_message(instance)

@receiver(post_save, sender=Recipe)
def post_save_recipe(sender, instance, created, **kwargs):
    if not hasattr(instance, '_post_save_triggered'):

        instance._post_save_triggered = True

        for recipe_ingredient in RecipeIngredient.objects.filter(recipe=instance):
            change_units(recipe_ingredient)

            recipe_ingredient._post_save_triggered = True
            recipe_ingredient.save()
            delattr(recipe_ingredient, '_post_save_triggered')

        instance.refresh_from_db()

        if created and int(instance.status) == Status.MODERATION:
            send_telegram_message(instance)

        delattr(instance, '_post_save_triggered')

@receiver(post_save, sender=RecipeIngredient)
def post_save_recipe_ingredient(sender, instance, **kwargs):
    if not hasattr(instance, '_post_save_triggered'):
        instance._post_save_triggered = True

        change_units(instance)

        delattr(instance, '_post_save_triggered')

@receiver(post_save, sender=RecipeStep)
def post_save_recipe_step(sender, instance, created, **kwargs):
    if not hasattr(instance, '_post_save_triggered'):
        instance._post_save_triggered = True

        if created:
            if instance.image:
                instance.image_watermark = add_watermark(instance.image)
                instance.save(update_fields=["image_watermark"])

        delattr(instance, '_post_save_triggered')


@receiver(post_save, sender=RecipeReview)
def post_save_review(sender, instance, **kwargs):
    instance.recipe.save()

@receiver(post_delete, sender=RecipeReview)
def post_delete_review(sender, instance, **kwargs):
    instance.recipe.save()

@receiver(post_delete, sender=RecipeComment)
def post_delete_comment(sender, instance, **kwargs):
    filtered_users_liked = User.objects.filter(liked_recipe_comments=instance)
    filtered_users_disliked = User.objects.filter(disliked_recipe_comments=instance)

    for user in filtered_users_liked:
        try:
            user.liked_recipe_comments.remove(instance)
        finally:
            user.save()

    for user in filtered_users_disliked:
        try:
            user.disliked_recipe_comments.remove(instance)
        finally:
            user.save()
