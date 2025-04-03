from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView

from categories.models import CategoryGroup, RecipeCategory
from news.models import News
from recipes.models import Recipe

paginate_by = 24


class NewsView(ListView):
    template_name = "news/articles.html"
    model = News
    paginate_by = paginate_by

    def get_queryset(self):
        queryset = super(NewsView, self).get_queryset()
        if (self.kwargs.get("slug", None)):
            category_obj = RecipeCategory.objects.get(slug=self.kwargs["slug"])
            queryset = queryset.filter(categories=category_obj)
        return queryset.order_by("-published_date")

    def get_context_data(self, **kwargs):
        context = super(NewsView, self).get_context_data(**kwargs)
        context['category_groups'] = CategoryGroup.objects.all()
        context['active_news'] = True
        context["kwargs"] = self.kwargs

        for item in context["object_list"]:
            item.stars_on_count = item.rating
            item.stars_off_count = 5-item.rating
            item.published_date = item.published_date.strftime('%d.%m.%Y')

        if (self.kwargs.get("slug", None)):
            context["kwargs"]["slug_name"] = RecipeCategory.objects.get(slug=self.kwargs["slug"]).name
        return context

class CreateNewsView(TemplateView):
    template_name = "news/add_news.html"

class DetailNewsView(DetailView):
    template_name = "news/detail_news.html"
    model = News

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.views += 1
        self.object.save()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DetailNewsView, self).get_context_data(**kwargs)

        user = self.request.user

        context['stars_on_count'] = self.object.rating
        context['stars_off_count'] = 5 - self.object.rating
        context['published_date'] = self.object.published_date.strftime('%d.%m.%Y')

        context['category_groups'] = CategoryGroup.objects.all()
        context['news_side'] = News.objects.filter(visibility=1, status=1).select_related("author").prefetch_related("reviews").order_by("-published_date")[:10]
        for item in context['news_side']:
            item.stars_on_count = item.rating
            item.stars_off_count = 5 - item.rating
            item.published_date = item.published_date.strftime('%d.%m.%Y')

        context['recs_recipes'] = Recipe.objects.filter(categories__in=self.object.categories.all(), visibility=1, status=1).select_related("previews", "author").prefetch_related("recipeingredient_set", "reviews")[:10]
        if context['recs_recipes'].count() < 10:
            additional_items = Recipe.objects.filter(visibility=1, status=1).exclude(categories__in=self.object.categories.all()).select_related("previews", "author").prefetch_related("recipeingredient_set", "reviews")[:10-context['recs_recipes'].count()]
            context['recs_recipes'] = context['recs_recipes'] | additional_items
        if context['recs_recipes'].count() < 4:
            context['recs_recipes'] = None

        context['recs_news'] = News.objects.filter(categories__in=self.object.categories.all(), visibility=1, status=1).select_related("author").prefetch_related("reviews")[:10]
        if context['recs_news'].count() < 10:
            additional_items = News.objects.filter(visibility=1, status=1).exclude(categories__in=self.object.categories.all()).select_related("author").prefetch_related("reviews")[:10-context['recs_news'].count()]
            context['recs_news'] = context['recs_news'] | additional_items
        if context['recs_news'].count() < 4:
            context['recs_news'] = None
        else:
            for item in context['recs_news']:
                item.stars_on_count = item.rating
                item.stars_off_count = 5 - item.rating
                item.published_date = item.published_date.strftime('%d.%m.%Y')

        if user.is_authenticated and self.object.reviews.filter(author=user).exists():
            context["user_review_exists"] = 1
            context["user_review_rating"] = self.object.reviews.get(author=user).rating
        else:
            context["user_review_exists"] = 0

        comments = self.object.comments.filter(parent=None).order_by('-published_date')
        paginator = Paginator(comments, 2)  # 20 комментариев на страницу
        page_number = 1
        page_obj = paginator.get_page(page_number)

        context["comments"] = page_obj

        return context

def bluk_create_objects(request):
    original_obj = News.objects.last()
    duplicates = []
    for i in range(1, 30):
        original_obj.id = None
        duplicates += [original_obj]
    News.objects.bulk_create(duplicates)

    return HttpResponseRedirect(reverse('main'))
