from django.db.models.signals import post_save
from django.dispatch import receiver

from news.models import News


@receiver(post_save, sender=News)
def post_save_news(sender, instance, **kwargs):
    if not hasattr(instance, '_post_save_triggered'):
        instance._post_save_triggered = True

        instance.set_total_rating()

        delattr(instance, '_post_save_triggered')
