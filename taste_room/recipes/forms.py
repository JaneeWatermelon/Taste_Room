from random import choices

from django import forms
from django.forms import inlineformset_factory

from additions.views import Status, Visibility
from .models import Recipe, RecipePreview, RecipeIngredient, RecipeStep, RecipeCategory, RecipeComment, Difficulty, \
    Scipy


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

class RecipePreviewForm(forms.ModelForm):
    class Meta:
        model = RecipePreview
        fields = ['preview_1', 'preview_2', 'preview_3']
        widgets = {
            'preview_1': forms.FileInput(attrs={'accept': 'image/*'}),
            'preview_2': forms.FileInput(attrs={'accept': 'image/*'}),
            'preview_3': forms.FileInput(attrs={'accept': 'image/*'}),
        }


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
        'minlength': 350,
        'maxlength': 1000,
    }), required=False)
    description_card = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Придумайте мини-описание для карточки рецепта',
        'minlength': 30,
        'maxlength': 50,
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


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity', 'unit']
        widgets = {
            'quantity': forms.NumberInput(attrs={'step': '0.1'}),
            'unit': forms.Select(attrs={'class': 'unit-select'}),
        }


class RecipeStepForm(forms.ModelForm):
    class Meta:
        model = RecipeStep
        fields = ['image', 'text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'image': forms.FileInput(attrs={'accept': 'image/*'}),
        }


# FormSets для связанных моделей
RecipeIngredientFormSet = inlineformset_factory(
    Recipe, RecipeIngredient,
    form=RecipeIngredientForm,
    extra=1,
    can_delete=True
)

RecipeStepFormSet = inlineformset_factory(
    Recipe, RecipeStep,
    form=RecipeStepForm,
    extra=1,
    can_delete=True
)