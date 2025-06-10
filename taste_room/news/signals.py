from django.conf import settings
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.urls import reverse

from additions.views import Status
from news.models import News, NewsReview, NewsComment
from users.models import User
from additions.tasks import send_telegram_notification

def send_telegram_message(instance):
    item_url = reverse("news:detail", kwargs={
        "pk": instance.id,
        "slug": instance.slug,
    })
    message = (
        f"<b>Новая статья!</b>\n\n"
        f"📄 <b>Название:</b> {instance.title}\n"
        f"📃 <b>Мини-описание:</b> {instance.description_card}\n"
        f"👨‍🍳 Автор: {instance.author.username}\n\n"
        f"🔗 Ссылка: {settings.DOMAIN_NAME}{item_url}\n"
        f"🔗 Ссылка на админку: {settings.DOMAIN_NAME}/admin/recipes/recipe/{instance.id}/change/"
    )
    send_telegram_notification.delay(message)

@receiver(pre_save, sender=News)
def pre_save_news(sender, instance, **kwargs):
    if instance.pk:
        old_status = get_object_or_404(News, id=instance.id).status
        new_status = instance.status
        if int(new_status) == Status.MODERATION and int(old_status) != Status.MODERATION:
            send_telegram_message(instance)

@receiver(post_save, sender=News)
def post_save_news(sender, instance, created, **kwargs):
    if not hasattr(instance, '_post_save_triggered'):
        instance._post_save_triggered = True

        instance.set_total_rating()

        instance.refresh_from_db()

        if created and int(instance.status) == Status.MODERATION:
            send_telegram_message(instance)

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