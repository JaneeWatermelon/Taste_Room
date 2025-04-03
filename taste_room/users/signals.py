import random

from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver

from users.models import Review, Comment, User, DisplayNames
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

@receiver(post_save, sender=User)
def post_save_user(sender, instance, created, **kwargs):
    if not hasattr(instance, '_post_save_triggered'):
        instance._post_save_triggered = True

        if created:
            instance.name = DisplayNames.List[random.randint(0, 29)][1]
            instance.save()

        delattr(instance, '_post_save_triggered')

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

@receiver(post_delete, sender=Comment)
def post_delete_comment(sender, instance, **kwargs):
    instance_id = instance.id
    filtered_users_liked = User.objects.filter(liked_comments_id__icontains=instance_id)
    filtered_users_disliked = User.objects.filter(disliked_comments_id__icontains=instance_id)

    for user in filtered_users_liked:
        try:
            user.liked_comments_id.remove(instance_id)
        finally:
            user.save()

    for user in filtered_users_disliked:
        try:
            user.disliked_comments_id.remove(instance_id)
        finally:
            user.save()
