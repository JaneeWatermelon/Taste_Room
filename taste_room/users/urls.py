from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from users.views import (ProfileView, AuthorPageView, user_logout,
                         change_rating, delete_rating, comment_reaction_change,
                         load_more_comments, delete_comment,
                         create_comment, load_my_recipes, load_my_articles)

app_name = "users"

urlpatterns = [
    path('profile', ProfileView.as_view(), name="profile"),
    path('author/<slug:username>', AuthorPageView.as_view(), name="author"),

    path('logout', user_logout, name="logout"),

    path('ajax/change_rating', change_rating, name="change_rating_ajax"),
    path('ajax/delete_rating', delete_rating, name="delete_rating_ajax"),
    path('ajax/comment_reaction_change', comment_reaction_change, name="comment_reaction_change_ajax"),
    path('ajax/delete_comment', delete_comment, name="delete_comment_ajax"),
    path('ajax/load_more_comments', load_more_comments, name="load_more_comments_ajax"),
    path('ajax/load_my_recipes', load_my_recipes, name="load_my_recipes_ajax"),
    path('ajax/load_my_articles', load_my_articles, name="load_my_articles_ajax"),
    path('ajax/add_comment', create_comment, name="add_comment_ajax"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
