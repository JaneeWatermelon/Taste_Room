from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


def login_required_with_modal(view_func=None, login_url=settings.LOGIN_URL):
    def actual_decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                return view_func(request, *args, **kwargs)

            request.session['reloading'] = 'login_window'
            return redirect(login_url)

        return wrapper

    if view_func:
        return actual_decorator(view_func)
    return actual_decorator