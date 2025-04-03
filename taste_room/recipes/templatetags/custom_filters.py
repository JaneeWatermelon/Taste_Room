from django import template
from django.utils.timezone import timedelta

register = template.Library()

@register.filter
def short_timedelta(duration):
    total_seconds = int(duration.total_seconds())  # Общее количество секунд

    days = f"{duration.days} д " if duration.days else ""
    hours = f"{int(total_seconds / 3600)} ч " if int(total_seconds / 3600) else ""
    total_seconds %= 3600
    minutes = f"{int(total_seconds / 60)} мин " if int(total_seconds / 60) else ""

    return (days + hours + minutes).strip()

@register.filter
def repeat(n):
    return range(1, n+1)

@register.filter
def round_ingredient_count(n):
    if n == int(n):
        return int(n)
    return n

@register.filter
def published_date_minus(comments):
    return comments.order_by("-published_date")

