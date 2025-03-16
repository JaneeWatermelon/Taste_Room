from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from users.views import ProfileView, AuthorPageView, user_logout, change_rating, delete_rating

app_name = "users"

urlpatterns = [
    path('profile', ProfileView.as_view(), name="profile"),
    path('author/<slug:username>', AuthorPageView.as_view(), name="author"),

    path('logout', user_logout, name="logout"),
    path('ajax/change_rating', change_rating, name="change_rating_ajax"),
    path('ajax/delete_rating', delete_rating, name="delete_rating_ajax"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
