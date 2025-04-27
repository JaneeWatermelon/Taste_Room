from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import RecipeModelViewSet

app_name = "api"

router = DefaultRouter()
router.register(r'recipes', RecipeModelViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
