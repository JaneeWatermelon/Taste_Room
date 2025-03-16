from django.contrib import admin

from unfold.admin import ModelAdmin

from additions.models import Socials, MetaTag

@admin.register(Socials)
class SocialsAdmin(ModelAdmin):
    pass

@admin.register(MetaTag)
class MetaTagAdmin(ModelAdmin):
    list_display = ["url", "title", "description"]
