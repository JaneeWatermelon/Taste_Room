from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver

from users.models import Review
from recipes.models import Recipe
from news.models import News

def change_rating(instance):
    item = Recipe.objects.filter(reviews=instance)

    if item.exists():
        item.first().save()
    else:
        item = News.objects.filter(reviews=instance)
        if item.exists():
            return item.first().save()

@receiver(post_save, sender=Review)
def post_save_review(sender, instance, **kwargs):
    print("in post save users")
    change_rating(instance)

related_instance = None

@receiver(pre_delete, sender=Review)
def pre_delete_review(sender, instance, **kwargs):
    global related_instance
    print("in pre delete review")

    # Сохраняем связанный рецепт или новость
    item = Recipe.objects.filter(reviews=instance).first()
    if item:
        related_instance = item
    else:
        item = News.objects.filter(reviews=instance).first()
        if item:
            related_instance = item

@receiver(post_delete, sender=Review)
def post_delete_review(sender, instance, **kwargs):
    global related_instance
    print("in post delete review")

    if related_instance:
        related_instance.save()  # Вызываем save(), чтобы обновить рейтинг
        related_instance = None  # Очищаем переменную
