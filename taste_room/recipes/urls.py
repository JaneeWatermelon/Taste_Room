from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from recipes.views import (CategoryRecipesView, DetailRecipeView,
                           PopularRecipesView, SearchRecipesView,
                           add_ingredient_card_item, add_ingredient_item,
                           add_ready_photo, add_recipe_step,
                           bluk_create_objects, change_rating,
                           change_recipe_ingredients, change_status,
                           comment_reaction_change, comments_partial_view,
                           create_comment, delete_comment, delete_rating,
                           ingredient_autocomplete,
                           ingredient_cards_autocomplete, load_more_comments,
                           recipe_create_view, recipe_edit_view,
                           recipe_like_change)

app_name = "recipes"

urlpatterns = [
    path('', CategoryRecipesView.as_view(), name="index"),
    path('category/<slug:slug>', CategoryRecipesView.as_view(), name="category"),

    path('page/<int:page>', CategoryRecipesView.as_view(), name="paginator"),
    path('page/<int:page>/category/<slug:slug>', CategoryRecipesView.as_view(), name="paginator_category"),

    path('search/', SearchRecipesView.as_view(), name="search"),
    path('page/<int:page>/search/', SearchRecipesView.as_view(), name="paginator_search"),

    path('popular', PopularRecipesView.as_view(), name="popular"),
    path('popular/page/<int:page>', PopularRecipesView.as_view(), name="paginator_popular"),

    path('create', recipe_create_view, name="create"),
    path('<int:pk>/edit', recipe_edit_view, name="edit"),
    path('<int:pk>/<slug:slug>', DetailRecipeView.as_view(), name="detail"),

    path('ajax/change_rating', change_rating, name="change_rating_ajax"),
    path('ajax/delete_rating', delete_rating, name="delete_rating_ajax"),

    path('ajax/comment_reaction_change', comment_reaction_change, name="comment_reaction_change_ajax"),
    path('ajax/delete_comment', delete_comment, name="delete_comment_ajax"),
    path('ajax/load_more_comments', load_more_comments, name="load_more_comments_ajax"),
    path('ajax/add_comment', create_comment, name="add_comment_ajax"),
    path('comments_partial_view', comments_partial_view, name="comments_partial_view"),

    path('ajax/recipe_like', recipe_like_change, name="recipe_like_ajax"),
    path('ajax/recipe_portions', change_recipe_ingredients, name="recipe_portions_ajax"),

    path('ajax/ingredient-autocomplete/', ingredient_autocomplete, name='ingredient_autocomplete_ajax'),
    path('ajax/ingredient_cards_autocomplete/', ingredient_cards_autocomplete, name='ingredient_cards_autocomplete_ajax'),
    path('ajax/add_ingredient_item/', add_ingredient_item, name='add_ingredient_item_ajax'),
    path('ajax/add_ingredient_card_item/', add_ingredient_card_item, name='add_ingredient_card_item_ajax'),
    path('ajax/add_recipe_step/', add_recipe_step, name='add_recipe_step_ajax'),
    path('ajax/add_ready_photo/', add_ready_photo, name='add_ready_photo_ajax'),

    path('ajax/change_status', change_status, name="change_status_ajax"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += path('bluk_create_objects', bluk_create_objects),
