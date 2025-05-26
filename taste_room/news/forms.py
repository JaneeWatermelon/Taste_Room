from django import forms

from additions.views import Visibility
from categories.models import RecipeCategory
from news.models import NewsComment, News
from ckeditor.widgets import CKEditorWidget


class CreateNewsCommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Поделитесь своими мыслями',
    }), required=True)
    image = forms.ImageField(widget=forms.FileInput(attrs={
        'class': 'image_input',
        'accept': 'image/png,image/jpeg',
    }), required=False)

    class Meta:
        model = NewsComment
        fields = ['text', 'image']

class CreateNewsForm(forms.ModelForm):
    categories = forms.ModelMultipleChoiceField(
        queryset=RecipeCategory.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    title = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Введите название статьи',
        'class': 'with_marks',
        'minlength': 20,
        'maxlength': 40,
    }))
    content_start = forms.CharField(widget=CKEditorWidget(config_name="awesome_ckeditor"))
    content_middle = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Интересный факт, статистика или какая-то полезная информация',
        'class': 'with_marks',
        'minlength': 0,
        'maxlength': 200,
    }), required=False)
    content_end = forms.CharField(widget=CKEditorWidget(config_name="awesome_ckeditor"), required=False)
    description_card = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Придумайте мини-описание для карточки рецепта',
        'class': 'with_marks',
        'minlength': 30,
        'maxlength': 60,
    }))
    visibility = forms.CharField(widget=forms.RadioSelect(choices=Visibility.List))

    class Meta:
        model = News
        fields = [
            'title', 'description_card',
            'content_start', 'content_middle', 'content_end',
            'status', 'visibility', 'categories'
        ]
