import random

from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from additions.models import Socials
from users.models import DisplayNames, User


@receiver(post_save, sender=User)
def post_save_user(sender, instance, created, **kwargs):
    if not hasattr(instance, '_post_save_triggered'):
        instance._post_save_triggered = True

        display_names = DisplayNames()

        if created:
            instance.name = display_names.get_random_display_name()
            instance.socials = Socials.objects.create()
            instance.save()

        delattr(instance, '_post_save_triggered')
