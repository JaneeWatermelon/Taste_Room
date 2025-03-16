from django.db.models.signals import post_save
from django.dispatch import receiver
from recipes.models import Recipe, RecipeIngredient

def change_units(instance):
    unit = instance.unit
    quantity = instance.quantity

    print(unit)
    print(quantity)

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

        instance.set_total_rating()

        delattr(instance, '_post_save_triggered')

@receiver(post_save, sender=RecipeIngredient)
def post_save_recipe_ingredient(sender, instance, **kwargs):
    if not hasattr(instance, '_post_save_triggered'):
        instance._post_save_triggered = True

        change_units(instance)

        delattr(instance, '_post_save_triggered')
