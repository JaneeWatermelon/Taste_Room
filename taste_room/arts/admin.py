from django.contrib import admin

from unfold.admin import ModelAdmin

from arts.models import Art

@admin.register(Art)
class ArtAdmin(ModelAdmin):
    list_display = ["title", "url"]
