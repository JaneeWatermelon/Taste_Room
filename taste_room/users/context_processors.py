from users.forms import UserLoginForm, UserRegistrationForm, ChangePasswordForm


def registration_form(request):
    return {
        'registration_form': UserRegistrationForm(),  # Возвращаем не привязанную форму
    }
def login_form(request):
    return {
        'login_form': UserLoginForm(),  # Возвращаем не привязанную форму
    }
def change_password_form(request):
    return {
        'change_password_form': ChangePasswordForm(),  # Возвращаем не привязанную форму
    }