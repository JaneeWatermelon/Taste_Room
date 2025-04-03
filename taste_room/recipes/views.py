from decimal import Decimal

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, ListView

from recipes.models import Recipe, Ingredient
from news.models import News
from categories.models import RecipeCategory, CategoryGroup
from users.forms import CreateCommentForm

from django.db.models import prefetch_related_objects

paginate_by = 34

class MainView(TemplateView):
    template_name = "recipes/main.html"

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['ingredients'] = Ingredient.objects.all()[:12]
        all_recipes = Recipe.objects.filter(visibility=1, status=1).select_related("previews", "author").prefetch_related("recipeingredient_set", "reviews")
        context['recipes'] = all_recipes.order_by("-published_date")[:34]
        context['recipes_popular'] = all_recipes.order_by('-popularity')[:34]
        for item in context['recipes']:
            item.stars_on_count = item.rating
            item.stars_off_count = 5 - item.rating
        for item in context['recipes_popular']:
            item.stars_on_count = item.rating
            item.stars_off_count = 5 - item.rating

        context['recipes_1'] = context['recipes'][:24]
        context['recipes_2'] = context['recipes'][24:]
        context['recipes_popular_1'] = context['recipes_popular'][:24]
        context['recipes_popular_2'] = context['recipes_popular'][24:]

        context['articles'] = News.objects.filter(visibility=1, status=1).select_related("author").prefetch_related("reviews")[:10]
        for item in context['articles']:
            item.stars_on_count = item.rating
            item.stars_off_count = 5 - item.rating
            item.published_date = item.published_date.strftime('%d.%m.%Y')

        return context

class CategoryRecipesView(ListView):
    template_name = "recipes/category_recipes.html"
    model = Recipe
    paginate_by = paginate_by

    def get_queryset(self):
        queryset = super(CategoryRecipesView, self).get_queryset()
        if (self.kwargs.get("slug", None)):
            category_obj = RecipeCategory.objects.get(slug=self.kwargs["slug"])
            queryset = queryset.filter(categories=category_obj)
        for item in queryset:
            item.stars_on_count = item.rating
            item.stars_off_count = 5 - item.rating
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategoryRecipesView, self).get_context_data(**kwargs)
        context['category_groups'] = CategoryGroup.objects.all()
        context['recipes_1'] = context["object_list"][:24]
        context['recipes_2'] = context["object_list"][24:]
        context['active_recipes'] = True
        context["kwargs"] = self.kwargs

        if (self.kwargs.get("slug", None)):
            context["kwargs"]["slug_name"] = RecipeCategory.objects.get(slug=self.kwargs["slug"]).name

        return context

class SearchRecipesView(ListView):
    template_name = "recipes/search_recipes.html"
    model = Recipe
    paginate_by = paginate_by

    def get_queryset(self):
        # decoded_prompt = iri_to_uri(self.request.GET.get("q"))
        queryset = find_similar_recipes(self.request.GET.get("q")) + list(word_search_recipes(self.request.GET.get("q")))
        for item in queryset:
            item.stars_on_count = item.rating
            item.stars_off_count = 5 - item.rating
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SearchRecipesView, self).get_context_data(**kwargs)
        context['category_groups'] = CategoryGroup.objects.all()
        context['prompt'] = self.request.GET.get("q")

        return context

class PopularRecipesView(ListView):
    template_name = "recipes/popular_recipes.html"
    model = Recipe
    paginate_by = paginate_by

    def get_queryset(self):
        queryset = super(PopularRecipesView, self).get_queryset().order_by('-popularity')
        for item in queryset:
            item.stars_on_count = item.rating
            item.stars_off_count = 5 - item.rating
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PopularRecipesView, self).get_context_data(**kwargs)

        context['recipes_popular_1'] = context["object_list"][:24]
        context['recipes_popular_2'] = context["object_list"][24:]
        context['active_popular'] = True

        return context

class CreateRecipeView(TemplateView):
    template_name = "recipes/add_recipe.html"

class DetailRecipeView(DetailView):
    template_name = "recipes/detail_recipe.html"
    model = Recipe

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = self.request.user

        if self.object.status == 4:
            return context
        elif self.object.status in (2, 4):
            raise Http404
        else:
            context['category_groups'] = CategoryGroup.objects.prefetch_related("categories", "categories__children")
            context['stars_on_count'] = self.object.rating
            context['stars_off_count'] = 5 - self.object.rating

            context['recipe_calories_per_100g'] = self.object.calculate_calories_per_100g()
            context['recipe_ingredients'] = self.object.recipeingredient_set.all()

            context['side_articles'] = News.objects.filter(visibility=1, status=1).select_related("author").prefetch_related("reviews").order_by("-published_date")[:10]
            for item in context['side_articles']:
                item.stars_on_count = item.rating
                item.stars_off_count = 5-item.rating
                item.published_date = item.published_date.strftime('%d.%m.%Y')

            context['recs_recipes'] = list(
                (Recipe.objects.filter(categories__in=self.object.categories.all(), visibility=1, status=1)
                 .exclude(pk=self.object.pk))[:10].select_related("previews", "author").prefetch_related("recipeingredient_set", "recipeingredient_set__recipe", "recipeingredient_set__ingredient", "reviews")
            )
            if len(context['recs_recipes']) < 10:
                additional_items = list(
                    Recipe.objects.filter(visibility=1, status=1).exclude(categories__in=self.object.categories.all())[:10-len(context['recs_recipes'])]
                    .select_related("previews", "author").prefetch_related("recipeingredient_set", "recipeingredient_set__recipe", "recipeingredient_set__ingredient", "reviews")
                )
                context['recs_recipes'] = context['recs_recipes'] + additional_items
            if len(context['recs_recipes']) < 4:
                context['recs_recipes'] = None

            context['recs_news'] = list(
                News.objects.filter(categories__in=self.object.categories.all(), visibility=1, status=1)[:10]
                .select_related("author").prefetch_related("reviews")
            )
            if len(context['recs_news']) < 10:
                additional_items = list(
                    News.objects.filter(visibility=1, status=1).exclude(
                    categories__in=self.object.categories.all())[:10 - len(context['recs_news'])]
                    .select_related("author").prefetch_related("reviews")
                )
                context['recs_news'] = context['recs_news'] + additional_items
            if len(context['recs_news']) < 4:
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
            context["create_comment_form"] = CreateCommentForm()

        return context

    def get(self, request, *args, **kwargs):
        self.object = Recipe.objects.filter(id=self.kwargs.get("pk")).select_related("previews", "author").prefetch_related("recipeingredient_set", "reviews").get()
        context = self.get_context_data(object=self.object)
        if self.object.status == 4:
            self.template_name = "additions/error_moderator.html"
        return self.render_to_response(context)



def bluk_create_objects(request):
    original_obj = Recipe.objects.last()
    duplicates = []
    for i in range(1, 30):
        original_obj.id = None
        duplicates += [original_obj]
    Recipe.objects.bulk_create(duplicates)

    return HttpResponseRedirect(reverse('main'))

def recipe_like_change(request):
    if request.method == "POST":
        recipe_id = int(request.POST.get("recipe_id"))
        user = request.user

        if user.is_authenticated:
            if recipe_id in user.liked_recipes_id:
                user.liked_recipes_id.remove(recipe_id)
                user.save()
                return JsonResponse({"answer": "Рецепт удалён из понравившихся"})
            else:
                user.liked_recipes_id.append(recipe_id)
                user.save()
                return JsonResponse({"answer": "Рецепт добавлен в понравившиеся"})
        else:
            return JsonResponse({"answer": "Пользователь не авторизован"})

def change_recipe_ingredients(request):
    if request.method == "POST":
        new_portions = int(request.POST.get("new_portions"))
        view = DetailRecipeView()
        view.request = request  # Передаем request
        view.kwargs = {'pk': int(request.POST.get("recipe_id"))}  # Передаем ID рецепта (например, 1)

        # Инициализируем self.object
        view.object = view.get_object()

        recipe_ingredients = view.get_context_data()['recipe_ingredients']

        coefficient = Decimal(round(new_portions / view.object.portions, 1))

        updated_ingredients = []
        for item in recipe_ingredients:
            item.quantity *= coefficient  # Умножаем количество на коэффициент
            updated_ingredients.append({
                'title': item.ingredient.title,
                'quantity': round(float(item.quantity), 2),  # Округляем до 2 знаков
                'unit': item.unit,
                'icon': item.ingredient.icon.url if item.ingredient.icon else '',
            })

        # Возвращаем JSON-ответ
        return JsonResponse({
            "answer": f"Кол-во ингредиентов увеличилось в {coefficient} раза",
            'status': 'success',
            'ingredients': updated_ingredients,
        })


from Levenshtein import distance, ratio


def find_similar_recipes(search_prompt, threshold=10):
    all_recipes = Recipe.objects.all().select_related("previews", "author").prefetch_related("recipeingredient_set", "reviews")
    similar = []
    search_prompt = search_prompt.lower()

    for recipe in all_recipes:
        my_treshold = distance(search_prompt, recipe.title.lower())
        print(my_treshold)
        if my_treshold <= threshold:
            similar.append(recipe)

    return similar

def word_search_recipes(search_prompt):
    # 2. Поиск по словам
    words = search_prompt.split()
    word_q = Q()
    for word in words:
        word = word.lower()
        word_q |= Q(title__icontains=word) | Q(description_card__icontains=word) | Q(ingredients__title__icontains=word)
    word_results = Recipe.objects.filter(word_q)

    return word_results.select_related("previews", "author").prefetch_related("recipeingredient_set", "reviews")

