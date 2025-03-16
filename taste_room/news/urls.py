from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from news.views import CreateNewsView, DetailNewsView, NewsView, bluk_create_objects

app_name = "news"

urlpatterns = [
    path('', NewsView.as_view(), name="index"),
    path('category/<slug:slug>', NewsView.as_view(), name="category"),
    path('page/<int:page>', NewsView.as_view(), name="paginator"),
    path('page/<int:page>/category/<slug:slug>', NewsView.as_view(), name="paginator_category"),
    path('create', CreateNewsView.as_view(), name="create"),
    path('<int:pk>/<slug:slug>', DetailNewsView.as_view(), name="detail"),

    path('ckeditor/', include('ckeditor_uploader.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('bluk_create_objects', bluk_create_objects)]
