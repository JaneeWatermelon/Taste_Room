from django import forms
from news.models import NewsComment

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
