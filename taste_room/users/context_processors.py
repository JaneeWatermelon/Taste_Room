from users.forms import ChangePasswordForm, UserLoginForm, UserRegistrationForm


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
def user_liked_recipes(request):
    return {
        'user_liked_recipes': request.user.liked_recipes.all if request.user.is_authenticated else None,
    }
# def cache_timeout(request):
#     return {
#         'cache_timeout': 30,
#     }