from django import forms
from users.models import Comment

class CreateCommentForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Поделитесь своими мыслями',
    }), required=True)
    image = forms.ImageField(widget=forms.FileInput(attrs={
        'class': 'image_input',
        'accept': 'image/png,image/jpeg',
    }), required=False)

    class Meta:
        model = Comment
        fields = ['text', 'image']