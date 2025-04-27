from django.shortcuts import render
from rest_framework import viewsets

from recipes.models import Recipe
from recipes.serializers import RecipeSerializer


class RecipeModelViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
