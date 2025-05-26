from random import choices

from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from additions.views import Status, Visibility

from .models import (Difficulty, Recipe, RecipeCategory, RecipeComment, Scipy)


class CreateRecipeCommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Поделитесь своими мыслями',
    }), required=True)
    image = forms.ImageField(widget=forms.FileInput(attrs={
        'class': 'image_input',
        'accept': 'image/png,image/jpeg',
    }), required=False)

    class Meta:
        model = RecipeComment
        fields = ['text', 'image']

def validate_image_size(image):
    max_size = 1 * 1024 * 1024
    if image.size > max_size:
        raise ValidationError("Размер изображения не должен превышать 1 МБ")

class CreateRecipeForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=RecipeCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    difficulty = forms.ChoiceField(
        choices=Difficulty.List,
        widget=forms.Select,
        required=True
    )
    scipy = forms.ChoiceField(
        choices=Scipy.List,
        widget=forms.Select,
        required=True
    )
    title = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Введите название рецепта',
        'class': 'with_marks',
        'minlength': 20,
        'maxlength': 40,
    }))
    portions = forms.IntegerField(widget=forms.NumberInput(attrs={
        'placeholder': 'Введите кол-во порций',
        'min': 1,
        'max': 100,
    }), required=False)
    description_inner = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Придумайте описание к рецепту',
        'class': 'with_marks',
        'minlength': 350,
        'maxlength': 1000,
    }), required=False)
    description_card = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Придумайте мини-описание для карточки рецепта',
        'class': 'with_marks',
        'minlength': 30,
        'maxlength': 60,
    }), required=False)
    video_url_first = forms.URLField(widget=forms.URLInput(attrs={
        'placeholder': 'Введите ссылку на видео-рецепт',
    }), required=False)
    video_url_second = forms.URLField(widget=forms.URLInput(attrs={
        'placeholder': 'Введите запасную ссылку на видео-рецепт',
    }), required=False)
    visibility = forms.CharField(widget=forms.RadioSelect(choices=Visibility.List))

    class Meta:
        model = Recipe
        fields = [
            'title', 'description_inner', 'description_card',
            'video_url_first', 'video_url_second',
            'cook_time_full', 'cook_time_active',
            'portions', 'scipy', 'difficulty',
            'status', 'visibility', 'categories'
        ]
        widgets = {
            'cook_time_full': forms.TimeInput(attrs={'type': 'time'}),
            'cook_time_active': forms.TimeInput(attrs={'type': 'time'}),
            'description_inner': forms.Textarea(attrs={'rows': 4}),
        }