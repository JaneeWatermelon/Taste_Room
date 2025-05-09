from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from news.models import News, NewsReview, NewsComment
from users.models import User


@receiver(post_save, sender=News)
def post_save_news(sender, instance, **kwargs):
    if not hasattr(instance, '_post_save_triggered'):
        instance._post_save_triggered = True

        instance.set_total_rating()

        delattr(instance, '_post_save_triggered')

@receiver(post_save, sender=NewsReview)
def post_save_review(sender, instance, **kwargs):
    print("in post save users")

    instance.news.save()

@receiver(post_delete, sender=NewsReview)
def post_delete_review(sender, instance, **kwargs):
    instance.news.save()

@receiver(post_delete, sender=NewsComment)
def post_delete_comment(sender, instance, **kwargs):
    filtered_users_liked = User.objects.filter(liked_news_comments=instance)
    filtered_users_disliked = User.objects.filter(disliked_news_comments=instance)

    for user in filtered_users_liked:
        try:
            user.liked_news_comments.remove(instance)
        finally:
            user.save()

    for user in filtered_users_disliked:
        try:
            user.disliked_news_comments.remove(instance)
        finally:
            user.save()