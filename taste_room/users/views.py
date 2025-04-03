from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import TemplateView, DetailView

from recipes.models import Recipe
from users.models import User, Achievement, GeneralAchievementCondition, CategoryAchievement, Review, Comment
from news.models import News

per_page = 34

class ProfileView(TemplateView):
    template_name = "users/profile.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.extra_context = {}  # Гарантированная инициализация при создании view

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        user = self.request.user
        context["subscribers_count"] = len(user.subscribers_id)
        context["liked_recipes"] = Recipe.objects.filter(id__in=user.liked_recipes_id, status=1, visibility=1).select_related("previews", "author").prefetch_related("recipeingredient_set", "reviews")
        context["my_achivs"] = user.achivs
        context["my_recipes"] = Recipe.objects.filter(author=user, status=1, visibility=1).select_related("previews", "author").prefetch_related("recipeingredient_set", "reviews")
        context["my_articles"] = News.objects.filter(author=user, status=1, visibility=1).select_related("author").prefetch_related("reviews")
        for item in context['my_articles']:
            item.stars_on_count = item.rating
            item.stars_off_count = 5-item.rating
            item.published_date = item.published_date.strftime('%d.%m.%Y')
        context["subscriptions"] = User.objects.filter(id__in=user.subscriptions_id)

        context["multiple_use_achivs"] = {}
        for achiv_condition in GeneralAchievementCondition.objects.all():
            achivs = Achievement.objects.filter(condition_general=achiv_condition)
            if achivs.exists():
                context["multiple_use_achivs"][achiv_condition.title] = [achivs, achivs.count(), 3-achivs.count()]

        context["date_joined"] = user.date_joined.strftime('%d.%m.%Y')
        context["object"] = user

        if 'my_recipes' not in self.extra_context:
            self.extra_context['my_recipes'] = context["my_recipes"]

        context.update(self.extra_context)

        return context

    def reload_my_recipes(self, user_id, status):
        queryset = Recipe.objects.filter(author__id=user_id, status=status).select_related("previews", "author").prefetch_related("recipeingredient_set", "reviews")

        self.extra_context['my_recipes'] = queryset

        return queryset

class AuthorPageView(DetailView):
    template_name = "users/author_page.html"
    model = User

    def get_object(self, queryset=None):
        object = get_object_or_404(User, username=self.kwargs["username"])
        object.date_joined = object.date_joined.strftime('%d.%m.%Y')
        return object

    def get_context_data(self, **kwargs):
        context = super(AuthorPageView, self).get_context_data(**kwargs)
        user = self.object
        context["subscribers_count"] = len(user.subscribers_id)
        context["recipes"] = Recipe.objects.filter(id__in=user.liked_recipes_id, status=1, visibility=1).select_related("previews", "author").prefetch_related("recipeingredient_set", "reviews")
        context["published_recipes_count"] = context["recipes"].count()

        mult_use_category = get_object_or_404(CategoryAchievement, pk=1)
        one_use_category = get_object_or_404(CategoryAchievement, pk=2)
        context["one_use_achivs"] = user.achivs.filter(category=one_use_category)
        context["multiple_use_achivs"] = user.achivs.filter(category=mult_use_category)

        context["articles"] = News.objects.filter(author=user, status=1, visibility=1).select_related("author").prefetch_related("reviews")
        for item in context['articles']:
            item.stars_on_count = item.rating
            item.stars_off_count = 5 - item.rating
            item.published_date = item.published_date.strftime('%d.%m.%Y')
        context["published_news_count"] = context["articles"].count()

        return context

def change_rating(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            user = request.user
            item_type = request.POST.get("item_type")
            new_rating = int(request.POST.get("new_rating"))
            item_id = int(request.POST.get("item_id"))
            if item_type == "recipe":
                item = Recipe.objects.get(id=item_id)
            else:
                item = News.objects.get(id=item_id)

            review = item.reviews.filter(author=user)
            if review.exists():
                review = review.first()
                review.rating = new_rating
                review.save()
            else:
                review = Review.objects.create(author=user, rating=new_rating)
                item.reviews.add(review)
                item.save()
            return JsonResponse({
                "answer": "Отзыв успешно создан или изменён"
            })
        else:
            return JsonResponse({
                "answer": "Пользователь не авторизован"
            })

def delete_rating(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            user = request.user
            item_type = request.POST.get("item_type")
            item_id = int(request.POST.get("item_id"))
            if item_type == "recipe":
                item = Recipe.objects.get(id=item_id)
            else:
                item = News.objects.get(id=item_id)

            review = item.reviews.filter(author=user)
            if review.exists():
                review = review.first()
                review.delete()
            return JsonResponse({
                "answer": "Отзыв успешно удалён"
            })
        else:
            return JsonResponse({
                "answer": "Пользователь не авторизован"
            })

def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('main'))

def validate_image_extension(value):
    valid_extensions = ['png', 'jpeg', 'jpg']
    ext = value.name.lower().split('.')[-1]
    if not ext in valid_extensions:
        raise ValidationError('Разрешены только файлы с расширениями .png, .jpeg или .jpg.')

def create_comment(request):
    if request.method == "POST":
        print(request.POST)

        item_id = request.POST.get("item_id")

        text = request.POST.get("text")
        data_parent_id = request.POST.get("data_parent_id")

        if data_parent_id:
            parent = Comment.objects.get(id=data_parent_id)
            comment = Comment.objects.create(text=text, parent=parent, author=request.user)
        else:
            image = request.FILES.get("image")
            if image:
                validate_image_extension(image)
                comment = Comment.objects.create(text=text, image=image, author=request.user)
            else:
                comment = Comment.objects.create(text=text, author=request.user)

        item_type = request.POST.get("item_type", "recipe")
        if (item_type == "recipe"):
            item = Recipe.objects.get(id=item_id)
        else:
            item = News.objects.get(id=item_id)
        item.comments.add(comment)
        item.save()

        return JsonResponse({
            'answer': "Комментарий успешно создан",
        })

def delete_comment(request):
    if request.method == "POST":
        print(request.POST)

        comment_id = request.POST.get("comment_id")

        comment = Comment.objects.get(id=comment_id)

        comment.delete()

        return JsonResponse({
            'answer': "Комментарий успешно удалён",
        })

def comment_reaction_change(request):
    if request.method == "POST":
        comment_id = int(request.POST.get("comment_id"))
        reaction_type = request.POST.get("reaction_type")
        user = request.user

        comment = Comment.objects.get(id=comment_id)

        response = dict()

        if user.is_authenticated:
            if reaction_type == 'like':
                if comment_id in user.liked_comments_id:
                    user.liked_comments_id.remove(comment_id)
                    comment.likes -= 1

                    response["answer"] = "Комментарий удалён из понравившихся"
                else:
                    user.liked_comments_id.append(comment_id)
                    comment.likes += 1
                    try:
                        user.disliked_comments_id.remove(comment_id)
                        comment.dislikes -= 1
                    except:
                        pass

                    response["answer"] = "Комментарий добавлен в понравившиеся"
            elif reaction_type == 'dislike':
                if comment_id in user.disliked_comments_id:
                    user.disliked_comments_id.remove(comment_id)
                    comment.dislikes -= 1

                    response["answer"] = "Комментарий удалён из непонравившихся"
                else:
                    user.disliked_comments_id.append(comment_id)
                    comment.dislikes += 1
                    try:
                        user.liked_comments_id.remove(comment_id)
                        comment.likes -= 1
                    except:
                        pass

                    response["answer"] = "Комментарий добавлен в непонравившиеся"

            user.save()
            comment.save()
            return JsonResponse(response)
        else:
            return JsonResponse({"answer": "Пользователь не авторизован"})


def load_more_comments(request):
    object_id = request.GET.get('object_id')
    object_type = request.GET.get('object_type')
    page = request.GET.get('page')

    if object_type == 'recipe':
        item = get_object_or_404(Recipe, id=object_id)
    else:
        item = get_object_or_404(News, id=object_id)

    comments = item.comments.filter(parent=None).order_by('-published_date')

    paginator = Paginator(comments, 2)  # 20 комментариев на страницу
    page_obj = paginator.get_page(page)

    # Добавляем CSRF-токен в контекст
    context = {
        'comments': page_obj,
        'object': item,  # Передаем объект рецепта, если он используется в шаблоне
    }
    context.update(csrf(request))  # Добавляем CSRF-токен

    # Рендерим HTML для новых комментариев
    comments_html = render_to_string('users/comments_partial.html', context)

    return JsonResponse({
        'comments_html': comments_html,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    })


def load_my_recipes(request):
    if request.method == "GET":
        data_status = request.GET.get("data_status")
        user = request.user

        page = request.GET.get('page')

        recipes = Recipe.objects.filter(author=user, status=data_status).select_related("previews", "author").prefetch_related("recipeingredient_set", "reviews")

        paginator = Paginator(recipes, per_page)
        page_obj = paginator.get_page(page)

        context = {
            'my_recipes': page_obj,
            'object': user,
            'user': user,
        }

        # Рендерим HTML для новых комментариев
        html = render_to_string('users/my_recipes_partial.html', context)

        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'answer': "Данные успешно обновлены",
        })

def load_my_articles(request):
    if request.method == "GET":
        data_status = request.GET.get("data_status")
        user = request.user

        page = request.GET.get('page')

        articles = News.objects.filter(author=user, status=data_status).select_related("author").prefetch_related("reviews")
        for item in articles:
            item.stars_on_count = item.rating
            item.stars_off_count = 5-item.rating
            item.published_date = item.published_date.strftime('%d.%m.%Y')

        paginator = Paginator(articles, per_page)
        page_obj = paginator.get_page(page)

        context = {
            'my_articles': page_obj,
            'object': user,
            'user': user,
        }

        # Рендерим HTML для новых комментариев
        html = render_to_string('users/my_articles_partial.html', context)

        return JsonResponse({
            'html': html,
            'has_next': page_obj.has_next(),
            'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
            'answer': "Данные успешно обновлены",
        })

