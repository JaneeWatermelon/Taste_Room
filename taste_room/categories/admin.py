from django.contrib import admin

from unfold.admin import ModelAdmin

from categories.forms import CategoryGroupForm
from categories.models import RecipeCategory, CategoryGroup

@admin.register(RecipeCategory)
class RecipeCategoryAdmin(ModelAdmin):
    list_display = ["name", "slug", "parent"]
    readonly_fields = ['slug']

@admin.register(CategoryGroup)
class CategoryGroupAdmin(ModelAdmin):
    form = CategoryGroupForm
    list_display = ["title", "slug", "id"]
    readonly_fields = ['slug']
