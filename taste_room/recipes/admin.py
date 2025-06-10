from django.contrib import admin
from django.contrib.admin import ModelAdmin, TabularInline

from recipes.models import (Ingredient, Recipe, RecipeComment,
                            RecipeIngredient, RecipePreview, RecipeReview,
                            RecipeStep)

from additions.views import Status


@admin.register(RecipePreview)
class RecipePreviewAdmin(ModelAdmin):
    pass

class RecipeStepAdmin(TabularInline):
    model = RecipeStep
    extra = 0

class RecipeIngredientAdmin(TabularInline):
    model = RecipeIngredient
    extra = 0

class RecipeReviewAdmin(TabularInline):
    model = RecipeReview
    extra = 0

@admin.action(description="Сделать Публичными")
def make_recipes_published(modeladmin, request, queryset):
    queryset.update(status=Status.PUBLISHED)

@admin.action(description="Пересохранить")
def resave_recipes(modeladmin, request, queryset):
    for item in queryset:
        item.save()

@admin.action(description="Пересохранить шаги рецептов")
def resave_recipes_steps(modeladmin, request, queryset):
    for item in queryset:
        for recipestep in RecipeStep.objects.filter(recipe=item):
            recipestep.save()

@admin.register(Recipe)
class RecipeAdmin(ModelAdmin):
    list_display = ["title", "status", "visibility", "author", "published_date"]
    readonly_fields = ['slug']

    actions = [
        make_recipes_published,
        resave_recipes,
        resave_recipes_steps,
    ]

    inlines = [
        RecipeIngredientAdmin,
        RecipeStepAdmin,
        RecipeReviewAdmin,
    ]



@admin.register(RecipeComment)
class RecipeCommentAdmin(admin.ModelAdmin):
    list_display = ["author", "likes", "dislikes", "parent", "published_date", "id"]

import csv
from io import TextIOWrapper

from django import forms
from django.contrib import admin
from django.shortcuts import redirect, render
from django.urls import path


class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

@admin.register(Ingredient)
class IngredientAdmin(ModelAdmin):
    list_display = ["title", "slug", "calory_count", "weight_per_unit", "icon",]
    list_editable = ["icon",]
    change_list_template = "admin/ingredient_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.import_csv),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            form = CsvImportForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
                reader = csv.DictReader(csv_file)
                done_titles = list(Ingredient.objects.all().values_list("title", flat=True))
                for row in reader:
                    if row['title'] not in done_titles:
                        Ingredient.objects.create(
                            title=row['title'],
                            calory_count=row['calory_count'],
                            weight_per_unit=row['calory_count'],
                            # weight_per_unit=row['weight_per_unit'],
                        )
                        done_titles.append(row['title'])
                self.message_user(request, "Ингредиенты успешно импортированы.")
                return redirect("..")
        else:
            form = CsvImportForm()
        context = {"form": form}
        return render(request, "admin/csv_import_form.html", context)
