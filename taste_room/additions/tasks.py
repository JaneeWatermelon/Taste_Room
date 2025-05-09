from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


@shared_task
def send_email_code_task(email_code, email):
    splited_email = email.split("@")
    before_dog, after_dog = splited_email[0], splited_email[-1]
    last_part = before_dog[-1]
    before_dog = before_dog[:-1]
    first_part = before_dog[:2]
    formatted_email = first_part + "**" + last_part + "@" + after_dog
    html_content = render_to_string(
        "additions/email_code.html",
        context={
            "email_code": email_code,
            "email": formatted_email,
        },
    )
    mail = send_mail(
        "Сброс пароля - Комната Вкусов",
        f"Ваш код для смены пароля: {email_code}",
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
        html_message=html_content,
    )