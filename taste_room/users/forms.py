import re

from django import forms
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from additions.models import Socials
from additions.validators import validate_telegram_url, validate_vk_url, validate_pinterest_url, validate_youtube_url, \
    validate_rutube_url
from users.models import User


class UserRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Введите имя пользователя',
    }), required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Введите адрес электронной почты',
    }), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Введите пароль',
    }), required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password',]

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[-a-zA-Z0-9_]+$', username):
            self.add_error('username', "Username может содержать только латинские буквы, цифры, дефисы и подчёркивания.")
        else:
            return username

    def clean_password(self):
        password = self.cleaned_data.get('password')
        try:
            validate_password(password)
        except ValidationError as e:
            self.add_error('password', e)
        return password

class UserLoginForm(forms.ModelForm):
    username_or_email = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Введите почту или имя пользователя',
    }), required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Введите пароль',
    }), required=True)

    class Meta:
        model = User
        fields = ['username_or_email', 'password',]

class ChangePasswordForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Придумайте новый пароль',
    }), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Введите новый пароль ещё раз',
    }), required=True)

    class Meta:
        model = User
        fields = ['password1', 'password2',]

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        try:
            validate_password(password1)
        except ValidationError as e:
            self.add_error('password1', e)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        # Проверяем только совпадение паролей
        if password1 and password2 and password1 != password2:
            self.add_error('password2', ValidationError("Пароли не совпадают"))

        return password2

class ChangeUserForm(UserChangeForm):
    name = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': 'Введите отображаемое имя',
    }))
    description_profile = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Введите описание профиля',
        'maxlength': '512',
    }))
    description_recipe = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Введите описание в рецепте',
        'maxlength': '512',
    }))
    description_news = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Введите описание в статье',
        'maxlength': '512',
    }))

    telegram = forms.URLField(widget=forms.URLInput(attrs={
        'placeholder': 'https://t.me/your_user',
    }), required=False)
    telegram.validators.append(validate_telegram_url)

    vk = forms.URLField(widget=forms.URLInput(attrs={
        'placeholder': 'https://vk.com/your_user',
    }), required=False)
    vk.validators.append(validate_vk_url)

    pinterest = forms.URLField(widget=forms.URLInput(attrs={
        'placeholder': 'https://pinterest.com/your_user',
    }), required=False)
    pinterest.validators.append(validate_pinterest_url)

    youtube = forms.URLField(widget=forms.URLInput(attrs={
        'placeholder': 'https://youtube.com/your_channel',
    }), required=False)
    youtube.validators.append(validate_youtube_url)

    rutube = forms.URLField(widget=forms.URLInput(attrs={
        'placeholder': 'https://rutube.ru/channel/your_channel',
    }), required=False)
    rutube.validators.append(validate_rutube_url)

    class Meta:
        model = User
        fields = ["name", "description_profile", "description_recipe", "description_news",]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Инициализируем значения из связанной модели
        if hasattr(self.instance, 'socials'):
            socials = self.instance.socials
            self.fields['telegram'].initial = socials.telegram
            self.fields['vk'].initial = socials.vk
            self.fields['pinterest'].initial = socials.pinterest
            self.fields['youtube'].initial = socials.youtube
            self.fields['rutube'].initial = socials.rutube

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            # Сохраняем данные социальных сетей
            if hasattr(user, 'socials'):
                socials = user.socials
            else:
                socials = Socials()
                user.socials = socials

            user.save()

            socials.telegram = self.cleaned_data['telegram']
            socials.vk = self.cleaned_data['vk']
            socials.pinterest = self.cleaned_data['pinterest']
            socials.youtube = self.cleaned_data['youtube']
            socials.rutube = self.cleaned_data['rutube']

            socials.save()

        return user