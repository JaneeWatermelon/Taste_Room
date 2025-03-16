from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from recipes.views import (PopularRecipesView, CategoryRecipesView,
                           CreateRecipeView, DetailRecipeView,
                           bluk_create_objects, recipe_like_change,
                           change_recipe_ingredients)

app_name = "recipes"

urlpatterns = [
    path('', CategoryRecipesView.as_view(), name="index"),
    path('category/<slug:slug>', CategoryRecipesView.as_view(), name="category"),
    path('page/<int:page>', CategoryRecipesView.as_view(), name="paginator"),
    path('page/<int:page>/category/<slug:slug>', CategoryRecipesView.as_view(), name="paginator_category"),
    path('popular', PopularRecipesView.as_view(), name="popular"),
    path('popular/page/<int:page>', PopularRecipesView.as_view(), name="paginator_popular"),
    path('create', CreateRecipeView.as_view(), name="create"),
    path('<int:pk>/<slug:slug>', DetailRecipeView.as_view(), name="detail"),

    path('ajax/recipe_like', recipe_like_change, name="recipe_like_ajax"),
    path('ajax/recipe_portions', change_recipe_ingredients, name="recipe_portions_ajax"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += path('bluk_create_objects', bluk_create_objects),
