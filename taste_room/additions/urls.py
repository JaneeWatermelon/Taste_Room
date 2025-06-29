from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from additions.views import ErrorModeratorView

app_name = "additions"

urlpatterns = [
    path('', ErrorModeratorView.as_view(), name="index"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
