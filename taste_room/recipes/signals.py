import os

from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from recipes.models import (Recipe, RecipeComment, RecipeIngredient,
                            RecipeReview)
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


@receiver(post_save, sender=Recipe)
def post_save_recipe(sender, instance, **kwargs):
    if not hasattr(instance, '_post_save_triggered'):

        instance._post_save_triggered = True

        for recipe_ingredient in RecipeIngredient.objects.filter(recipe=instance):
            change_units(recipe_ingredient)

            recipe_ingredient._post_save_triggered = True
            recipe_ingredient.save()
            delattr(recipe_ingredient, '_post_save_triggered')

        delattr(instance, '_post_save_triggered')

@receiver(post_save, sender=RecipeIngredient)
def post_save_recipe_ingredient(sender, instance, **kwargs):
    if not hasattr(instance, '_post_save_triggered'):
        instance._post_save_triggered = True

        change_units(instance)

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
