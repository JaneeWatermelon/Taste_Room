from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now, timedelta

from additions.models import EmailCode

# @receiver(post_save, sender=EmailCode)
# def post_save_email_code(sender, instance, created, **kwargs):
#     if not hasattr(instance, '_post_save_triggered'):
#         instance._post_save_triggered = True
#
#         if created:
#             instance.expiration = now() + timedelta(days=1)
#             instance.save()
#
#         delattr(instance, '_post_save_triggered')
