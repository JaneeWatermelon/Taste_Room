from django.contrib.auth import logout
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, DetailView

from recipes.models import Recipe
from users.models import User, Achievement, GeneralAchievementCondition, CategoryAchievement, Review
from news.models import News


class ProfileView(DetailView):
    template_name = "users/profile.html"
    model = User

    def get_object(self, queryset=None):
        object = self.request.user
        object.date_joined = object.date_joined.strftime('%d.%m.%Y')
        return object

    def get_context_data(self, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)
        user = self.object
        context["subscribers_count"] = len(user.subscribers_id)
        context["liked_recipes"] = Recipe.objects.filter(id__in=user.liked_recipes_id, status=1, visibility=1)
        context["my_achivs"] = user.achivs
        context["my_recipes"] = Recipe.objects.filter(author=user)
        context["my_articles"] = News.objects.filter(author=user)
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

        return context

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
        context["recipes"] = Recipe.objects.filter(id__in=user.liked_recipes_id, status=1, visibility=1)
        context["published_recipes_count"] = context["recipes"].count()

        mult_use_category = get_object_or_404(CategoryAchievement, pk=1)
        one_use_category = get_object_or_404(CategoryAchievement, pk=2)
        context["one_use_achivs"] = user.achivs.filter(category=one_use_category)
        context["multiple_use_achivs"] = user.achivs.filter(category=mult_use_category)

        context["articles"] = News.objects.filter(author=user, status=1, visibility=1)
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
