import django
from debug_toolbar.toolbar import debug_toolbar_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.urls import include, path

from additions.views import Error404View
from recipes.views import MainView

django.conf.urls.handler404 = Error404View.as_view()

def cleanup_unused_images(request):
    if request.method == 'POST':
        used_images = request.POST.getlist('used_images[]')
        all_images = default_storage.listdir('ckeditor/')[1]

        for image in all_images:
            if image not in used_images:
                default_storage.delete(f'ckeditor/{image}')

        return JsonResponse({'status': 'ok'})

    return JsonResponse({'status': 'error'}, status=400)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view(), name="main"),
    path('recipes/', include("recipes.urls", namespace="recipes")),
    path('news/', include("news.urls", namespace="news")),
    path('users/', include("users.urls", namespace="users")),
    path('api/', include("api.urls", namespace="api")),

    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('ckeditor/cleanup/', cleanup_unused_images, name='ckeditor_cleanup'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('error_404', Error404View.as_view(), name='error_404')]
    urlpatterns += debug_toolbar_urls()