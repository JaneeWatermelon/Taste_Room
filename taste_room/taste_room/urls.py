import django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls

from recipes.views import MainView
from additions.views import Error404View

django.conf.urls.handler404 = Error404View.as_view()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view(), name="main"),
    path('recipes/', include("recipes.urls", namespace="recipes")),
    path('news/', include("news.urls", namespace="news")),
    path('users/', include("users.urls", namespace="users")),
    path('api/', include("api.urls", namespace="api")),

    path('ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('error_404', Error404View.as_view(), name='error_404')]
    urlpatterns += debug_toolbar_urls()