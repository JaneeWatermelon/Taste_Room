from django.contrib import admin
from django.contrib.admin import ModelAdmin

from additions.models import EmailCode, MetaTag, Socials


@admin.register(Socials)
class SocialsAdmin(ModelAdmin):
    pass

@admin.register(MetaTag)
class MetaTagAdmin(ModelAdmin):
    list_display = ["url", "title", "description"]

@admin.register(EmailCode)
class EmailCodeAdmin(ModelAdmin):
    list_display = ["email", "expiration", "code"]
