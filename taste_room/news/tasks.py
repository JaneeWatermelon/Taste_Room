from celery import shared_task
from django.shortcuts import get_object_or_404
from django.utils.timezone import now, timedelta

from additions.views import Status
from news.models import News


@shared_task
def check_moderation_status():
    expired_time = now() - timedelta(minutes=10)
    expired_items = News.objects.filter(
        status=Status.MODERATION,
        status_updated_at__lte=expired_time
    )

    expired_items.update(status=Status.PUBLISHED)