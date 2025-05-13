from django.contrib import admin
from django.contrib.admin import ModelAdmin

from categories.forms import CategoryGroupForm
from categories.models import CategoryGroup, RecipeCategory


@admin.register(RecipeCategory)
class RecipeCategoryAdmin(ModelAdmin):
    list_display = ["name", "slug", "parent"]
    readonly_fields = ['slug']
    ordering = ["parent", "name"]

@admin.register(CategoryGroup)
class CategoryGroupAdmin(ModelAdmin):
    form = CategoryGroupForm
    list_display = ["title", "slug", "id"]
    readonly_fields = ['slug']
