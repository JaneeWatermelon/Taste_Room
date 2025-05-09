from django import template
from django.forms import CheckboxInput
from django.utils.timezone import timedelta

register = template.Library()

@register.filter
def short_timedelta(duration):
    total_seconds = int(duration.total_seconds())  # Общее количество секунд

    days = f"{duration.days} д " if duration.days else ""
    hours = f"{int(total_seconds / 3600)} ч " if int(total_seconds / 3600) else ""
    total_seconds %= 3600
    minutes = f"{int(total_seconds / 60)} мин " if int(total_seconds / 60) else ""

    result = (days + hours + minutes).strip()

    return result if result != "" else "Не указано"

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

@register.filter
def get_first_value(dictionary, key):
    return dictionary.get(key)[0]

@register.filter
def get_second_value(dictionary, key):
    return dictionary.get(key)[1]

@register.filter
def get_checkbox(field, category_id):
    widget = field.field.widget
    attrs = widget.build_attrs({'id': f'id_{field.name}_{category_id}'})
    is_checked = category_id in field.value() if field.value() else False
    return CheckboxInput(attrs, check_test=lambda v: is_checked).render(
        field.name,
        category_id
    )

@register.filter
def _int(n):
    return int(n)

@register.filter
def DHMS(time_delta): # Days Hours Minutes Seconds
    if not isinstance(time_delta, timedelta):
        return [0, 0, 0, 0]

    total_seconds = int(time_delta.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return [days, hours, minutes, seconds]

@register.filter
def iso_timedelta(time_delta):
    days, hours, minutes, seconds = DHMS(time_delta)

    result = "PT"
    if days > 0:
        result += str(days) + "D"
    if hours > 0:
        result += str(hours) + "H"
    if minutes > 0:
        result += str(minutes) + "M"

    return result



