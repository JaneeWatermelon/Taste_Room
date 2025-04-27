from django.contrib import admin
from django.contrib.admin import ModelAdmin

from news.models import News, NewsComment, NewsReview


@admin.register(News)
class NewsAdmin(ModelAdmin):
    list_display = ["title", "status", "visibility", "author", "published_date"]
    readonly_fields = ['slug']

@admin.register(NewsComment)
class NewsCommentAdmin(admin.ModelAdmin):
    list_display = ["author", "likes", "dislikes", "parent", "published_date", "id"]

@admin.register(NewsReview)
class NewsReviewAdmin(admin.ModelAdmin):
    list_display = ["author", "rating",]
