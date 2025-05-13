from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import (Http404, HttpResponseForbidden, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.timezone import now, timedelta
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView, TemplateView

from additions.models import EmailCode
from additions.views import get_recipes_author_page, get_news_author_page, set_meta_tags
from news.models import News
from recipes.models import Recipe
from users.forms import (ChangePasswordForm, ChangeUserForm, UserLoginForm,
                         UserRegistrationForm)
from users.models import (Achievement, CategoryAchievement, Color,
                          GeneralAchievementCondition, User)
from  additions.tasks import send_email_code_task

per_page = 100

html_errors_template = "users/auth_errors_partial.html"
empty_html_template = 'additions/empty_block.html'

def format_form_errors(form_errors, form):
    formatted_errors = []

    for field, errors in form_errors.items():
        # Получаем человекочитаемое название поля
        field_name = form.fields[field].label or field

        for error in errors:
            if error['code'] == 'required':
                formatted_errors += [{"message": f"Поле {field_name} является обязательным"}]
            elif error['code'] == 'unique':
                formatted_errors += [error]
            else:
                formatted_errors += [error]

    return formatted_errors

class ProfileView(TemplateView):
    template_name = "users/profile.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = ChangeUserForm(self.request.POST, instance=self.request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
        return render(request, 'users/profile.html', {'settings_form': form})

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        user = self.request.user
        context["liked_recipes"] = user.liked_recipes.filter(status=1, visibility=1).select_related("previews", "author").prefetch_related("recipereview_set", "recipeingredient_set", "recipeingredient_set__ingredient",)

        context["my_recipes"] = Recipe.objects.filter(author=user, status=1).select_related("previews", "author").prefetch_related("recipereview_set", "recipeingredient_set", "recipeingredient_set__ingredient",)
        context["my_articles"] = News.objects.filter(author=user, status=1).select_related("author").prefetch_related("newsreview_set")

        context["fon_colors"] = Color.objects.all()

        context["multiple_use_achivs"] = {}
        for achiv_condition in GeneralAchievementCondition.objects.all():
            achivs = Achievement.objects.filter(condition_general=achiv_condition)
            if achivs.exists():
                context["multiple_use_achivs"][achiv_condition.title] = [achivs, achivs.count(), 3-achivs.count()]

        context["object"] = user
        context["settings_form"] = ChangeUserForm(instance=user)

        return context

class AuthorPageView(DetailView):
    template_name = "users/author_page.html"
    model = User

    def get_object(self, queryset=None):
        object = get_object_or_404(User, username=self.kwargs["username"])

        item_preview = object.avatar if object.avatar else None
        object_name = object.name if object.name else object.username

        set_meta_tags(
            self.request,
            f"Автор: {object_name} | Рецепты на «Комната Вкуса»",
            f"Все рецепты от {object_name} с подробными инструкциями и фото. Подпишитесь, чтобы не пропустить новое!",
            f"{object_name} — авторские рецепты",
            f"Готовьте по рецептам {object_name} — только проверенные блюда.",
            image=item_preview,
        )

        return object

    def get_context_data(self, **kwargs):
        context = super(AuthorPageView, self).get_context_data(**kwargs)
        user = self.request.user
        author = self.object
        context["recipes"] = get_recipes_author_page(user, author)
        context["published_recipes_count"] = context["recipes"].count()

        context["articles"] = get_news_author_page(user, author)
        context["published_news_count"] = context["articles"].count()

        mult_use_category = get_object_or_404(CategoryAchievement, pk=1)
        one_use_category = get_object_or_404(CategoryAchievement, pk=2)
        context["one_use_achivs"] = author.achivs.filter(category=one_use_category)
        context["multiple_use_achivs"] = author.achivs.filter(category=mult_use_category)

        context["user"] = user

        return context

def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('main'))

def validate_image_extension(value):
    valid_extensions = ['png', 'jpeg', 'jpg']
    ext = value.name.lower().split('.')[-1]
    if not ext in valid_extensions:
        raise ValidationError('Разрешены только файлы с расширениями .png, .jpeg или .jpg.')

def _prepare_pagination_data(user, data_status, model=Recipe, page=1):
    recipes = model.objects.filter(author=user, status=data_status)

    paginator = Paginator(recipes, per_page)
    page_obj = paginator.get_page(page)

    context = {
        'page_obj': page_obj,
        'object': user,
        'user': user,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator,
    }

    # Рендерим HTML для новых комментариев
    html = render_to_string('users/pagination_partial.html', context)

    return {
        'html': html,
        'answer': "Данные успешно обновлены",
    }

def _prepare_recipes_data(user, data_statuses, page=1):
    recipes = Recipe.objects.filter(pk=0)
    for status in data_statuses:
        recipes |= Recipe.objects.filter(author=user, status=status).select_related("previews", "author").prefetch_related("recipereview_set", "recipeingredient_set", "recipeingredient_set__ingredient",)

    paginator = Paginator(recipes, per_page)
    page_obj = paginator.get_page(page)

    context = {
        'recipes_list': page_obj,
        'is_buttons': True,
        'object': user,
        'user': user,
    }

    # Рендерим HTML для новых комментариев
    html = render_to_string('recipes/includes/recipe_cards.html', context)

    return {
        'html': html,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'answer': "Данные успешно обновлены",
    }

@require_GET
def load_my_recipes(request):
    data_status = request.GET.get("data_status")
    user = request.user
    page = request.GET.get('page', 1)

    data_statuses = data_status.split(",")

    return JsonResponse(_prepare_recipes_data(user, data_statuses, page))


def _prepare_articles_data(user, data_statuses, page=1):
    articles = News.objects.filter(pk=0)
    print(data_statuses)
    for status in data_statuses:
        articles |= News.objects.filter(author=user, status=status).select_related("author")

    paginator = Paginator(articles, per_page)
    page_obj = paginator.get_page(page)

    context = {
        'news_list': page_obj,
        'is_buttons': True,
        'object': user,
        'user': user,
    }

    html = render_to_string('news/includes/news_cards.html', context)

    return {
        'html': html,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'answer': "Данные успешно обновлены",
    }

@require_GET
def load_my_articles(request):
    data_status = request.GET.get("data_status")
    user = request.user
    page = request.GET.get('page', 1)

    data_statuses = data_status.split(",")

    return JsonResponse(_prepare_articles_data(user, data_statuses, page))

@require_POST
def sub_unsub(request):
    user = request.user
    data_id = request.POST.get("data_id")
    data_type = request.POST.get("data_type")

    sub_user = get_object_or_404(User, id=data_id)

    user_subscriptions_exists = user.subscriptions.filter(id=data_id).exists()

    if data_type == 'sub':
        if not user_subscriptions_exists:
            user.subscriptions.add(sub_user)
    elif data_type == 'unsub':
        if user_subscriptions_exists:
            user.subscriptions.remove(sub_user)

    user.save()
    sub_user.save()

    return JsonResponse({
        "answer": "Подписки успешно изменены",
        "subs_count": sub_user.subscribers.count(),
    })

@require_GET
def get_search_subs(request):
    user = request.user
    tag = request.GET.get("tag")
    query = User.objects.filter(username__icontains=tag).exclude(id=user.id)

    context = {
        'tag_users': query,
        'object': user,
        'user': user,
    }

    # Рендерим HTML для новых комментариев
    html = render_to_string('users/search_subs_partial.html', context)

    return JsonResponse({
        "answer": "Пользователи содержащие указанный тег получены",
        "html": html,
    })

@require_POST
def change_back_fon(request):
    color_id = request.POST.get("data_id")
    user = request.user

    if color_id:
        color = get_object_or_404(Color, id=color_id)

        user.background_color = color
        user.save()

    return JsonResponse({
        'answer': "Цвет фона успешно изменён",
        'background_hash': color.hash,
        'text_hash': color.text_hash,
    })

@require_POST
def change_profile_image(request):
    image = request.FILES.get("image")
    user = request.user
    if image:
        user.avatar = image
        user.save()
        return JsonResponse({
            "answer": "Аватар пользователя успешно изменён"
        })
    else:
        user.avatar = None
        user.save()
        return JsonResponse({
            "answer": "Аватар пользователя сброшен"
        })

@require_POST
def change_profile_current_achiv(request):
    item_id = request.POST.get("item_id")
    active = request.POST.get("active")
    user = request.user

    achiv = get_object_or_404(Achievement, id=item_id)

    if active == "true" and user.achivs.filter(id=item_id).exists():
        user.choosed_achiv = achiv
    else:
        user.choosed_achiv = None
    user.save()

    return JsonResponse({
        "answer": "Текущее достижение пользователя успешно изменено"
    })

@require_POST
def user_registration(request):
    form = UserRegistrationForm(request.POST)

    if form.is_valid():
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')

        user = User.objects.create(username=username, email=email)

        user.set_password(password)
        user.save()
        return JsonResponse({
            "answer": "Пользователь успешно создан",
        })
    else:
        formatted_errors = format_form_errors(form.errors.get_json_data(), form)
        return JsonResponse({
            "html_errors": render_to_string(html_errors_template, context={
                "errors": list(
                    {"message": error.get('message', 'Неверные данные формы')} for error in formatted_errors
                ),
            }),
        }, status=400)

@require_POST
def user_login(request):
    form = UserLoginForm(request.POST)

    if form.is_valid():
        username_or_email = form.cleaned_data.get('username_or_email')
        password = form.cleaned_data.get('password')

        if User.objects.filter(username=username_or_email).exists():
            user = authenticate(request, username=username_or_email, password=password)
        elif User.objects.filter(email=username_or_email).exists():
            user = User.objects.get(email=username_or_email)
            user = authenticate(request, username=user.username, password=password)
        else:
            user = None

        if user is not None:
            login(request, user)
            return JsonResponse({
                "answer": "Пользователь успешно авторизован",
            })
        else:
            return JsonResponse({
                "html_errors": render_to_string(html_errors_template, context={
                    "errors": [
                        {"message": "Неверные Имя пользователя(почта) или Пароль"},
                    ]
                }),
            }, status=401)
    else:
        formatted_errors = format_form_errors(form.errors.get_json_data(), form)
        return JsonResponse({
            "html_errors": render_to_string(html_errors_template, context={
                "errors": list(
                    {"message": error.get('message', 'Неверные данные формы')} for error in formatted_errors
                ),
            }),
        }, status=400)

@require_POST
def send_email_code(request):
    email = request.POST.get("email")

    for item in EmailCode.objects.filter(email=email):
        item.delete()

    try:
        email_code_obj = EmailCode.objects.create(email=email)

        send_email_code_task.delay(email_code_obj.code, email)

        return JsonResponse({
            "answer": "Письмо успешно отправлено",
        })
    except Exception as e:
        return JsonResponse({
            "html_errors": render_to_string(html_errors_template, context={
                "errors": [
                    {"message": "Почта указана неверно"}
                ],
            }),
        }, status=400)

@require_POST
def continue_reset_password(request):
    email = request.POST.get("email")
    code = request.POST.get("code")

    email_code_obj = EmailCode.objects.filter(email=email)
    if email_code_obj.exists():
        email_code_obj = email_code_obj.last()
        if str(email_code_obj.code) == code and email_code_obj.is_expired() == False:
            email_code_obj.accepted = True
            email_code_obj.save()

            request.session['reset_password_email'] = email
            request.session.modified = True

            return JsonResponse({
                "answer": "Почта успешно подтверждена",
            })
        else:
            if email_code_obj.is_expired():
                return JsonResponse({
                    "html_errors": render_to_string(html_errors_template, context={
                        "errors": [
                            {"message": "Cрок действия кода подтверждения был истечён"}
                        ],
                    }),
                }, status=400)
            else:
                return JsonResponse({
                    "html_errors": render_to_string(html_errors_template, context={
                        "errors": [
                            {"message": "Неправильный код доступа"}
                        ],
                    }),
                }, status=400)
    else:
        print("in else continue_reset_password")
        return JsonResponse({
            "html_errors": render_to_string(html_errors_template, context={
                "errors": [
                    {"message": "Код подтверждения ещё ни разу не был отправлен"}
                ],
            }),
        }, status=400)

@require_POST
def final_change_password(request):

    form = ChangePasswordForm(request.POST)

    email = request.session.get('reset_password_email')

    if form.is_valid():
        if email != None:
            email_code_obj = EmailCode.objects.filter(email=email)
            if email_code_obj.exists():
                email_code_obj = email_code_obj.last()

                password1 = form.cleaned_data.get('password1')
                password2 = form.cleaned_data.get('password2')

                if password1 == password2 and email_code_obj.accepted:
                    user = get_object_or_404(User, email=email)

                    user.set_password(password1)
                    user.save()

                    email_code_obj.delete()

                    del request.session['reset_password_email']

                    return JsonResponse({
                        "success": "True",
                        "answer": "Пароль успешно изменён",
                    })
                else:
                    if not email_code_obj.accepted:
                        return JsonResponse({
                            "html_errors": render_to_string(html_errors_template, context={
                                "errors": [
                                    {"message": "Почта не была подтверждена"}
                                ],
                            }),
                        }, status=400)
                    else:
                        return JsonResponse({
                            "html_errors": render_to_string(html_errors_template, context={
                                "errors": [
                                    {"message": "Пароли не совпадают"}
                                ],
                            }),
                        }, status=400)
            else:
                return JsonResponse({
                    "html_errors": render_to_string(html_errors_template, context={
                        "errors": [
                            {"message": "Код подтверждения ещё ни разу не был отправлен"}
                        ],
                    }),
                }, status=400)
        else:
            return JsonResponse({
                "html_errors": render_to_string(html_errors_template, context={
                    "errors": [
                        {"message": "Почта не была подтверждена"}
                    ],
                }),
            }, status=400)
    else:
        formatted_errors = format_form_errors(form.errors.get_json_data(), form)
        return JsonResponse({
            "html_errors": render_to_string(html_errors_template, context={
                "errors": list(
                    {"message": error.get('message', 'Неверные данные формы')} for error in formatted_errors
                ),
            }),
        }, status=400)



