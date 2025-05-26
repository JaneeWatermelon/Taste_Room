from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from news.views import (DetailNewsView, NewsView,
                        bluk_create_objects, change_rating, change_status,
                        comment_reaction_change, comments_partial_view,
                        create_comment, delete_comment, delete_rating,
                        load_more_comments, news_create_view, news_edit_view, news_delete)

app_name = "news"

urlpatterns = [
    path('', NewsView.as_view(), name="index"),
    path('category/<slug:slug>', NewsView.as_view(), name="category"),
    path('page/<int:page>', NewsView.as_view(), name="paginator"),
    path('page/<int:page>/category/<slug:slug>', NewsView.as_view(), name="paginator_category"),

    path('create', news_create_view, name="create"),
    path('<int:pk>/edit', news_edit_view, name="edit"),
    path('<int:pk>/<slug:slug>', DetailNewsView.as_view(), name="detail"),

    path('ajax/change_rating', change_rating, name="change_rating_ajax"),
    path('ajax/delete_rating', delete_rating, name="delete_rating_ajax"),
    path('ajax/news_delete', news_delete, name="news_delete_ajax"),

    path('ajax/comment_reaction_change', comment_reaction_change, name="comment_reaction_change_ajax"),
    path('ajax/delete_comment', delete_comment, name="delete_comment_ajax"),
    path('ajax/load_more_comments', load_more_comments, name="load_more_comments_ajax"),
    path('ajax/add_comment', create_comment, name="add_comment_ajax"),
    path('comments_partial_view', comments_partial_view, name="comments_partial_view"),

    path('ajax/change_status', change_status, name="change_status_ajax"),

    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('bluk_create_objects', bluk_create_objects)]
