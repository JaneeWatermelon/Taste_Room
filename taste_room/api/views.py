from django.shortcuts import render
from rest_framework import viewsets
from recipes.serializers import RecipeSerializer
from recipes.models import Recipe

class RecipeModelViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
