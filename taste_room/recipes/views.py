from decimal import Decimal

from django.db.models import Case, When, Value, IntegerField
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, DetailView, ListView

from recipes.models import Recipe, Ingredient
from news.models import News
from categories.models import RecipeCategory, CategoryGroup
from users.models import Review

paginate_by = 24

class MainView(TemplateView):
    template_name = "recipes/main.html"

    def get_context_data(self, **kwargs):
        context = super(MainView, self).get_context_data(**kwargs)
        context['ingredients'] = Ingredient.objects.all()[:12]
        context['recipes'] = Recipe.objects.filter(visibility=1, status=1)
        for item in context['recipes']:
            item.stars_on_count = item.rating
            item.stars_off_count = 5-item.rating

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
            item.published_date = item.published_date.strftime('%d.%m.%Y')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(CategoryRecipesView, self).get_context_data(**kwargs)
        context['category_groups'] = CategoryGroup.objects.all()
        context['active_recipes'] = True
        context["kwargs"] = self.kwargs

        if (self.kwargs.get("slug", None)):
            context["kwargs"]["slug_name"] = RecipeCategory.objects.get(slug=self.kwargs["slug"]).name

        return context

class PopularRecipesView(ListView):
    template_name = "recipes/popular_recipes.html"
    model = Recipe
    paginate_by = paginate_by

    def get_queryset(self):
        queryset = super(PopularRecipesView, self).get_queryset()
        for item in queryset:
            item.stars_on_count = item.rating
            item.stars_off_count = 5 - item.rating
            item.published_date = item.published_date.strftime('%d.%m.%Y')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PopularRecipesView, self).get_context_data(**kwargs)
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
        context['category_groups'] = CategoryGroup.objects.all()
        context['stars_on_count'] = self.object.rating
        context['stars_off_count'] = 5 - self.object.rating
        context['recipe_ingredients'] = self.object.recipeingredient_set.all()
        context['articles'] = News.objects.filter(visibility=1, status=1)
        for item in context['articles']:
            item.stars_on_count = item.rating
            item.stars_off_count = 5-item.rating
            item.published_date = item.published_date.strftime('%d.%m.%Y')

        context['recs_recipes'] = Recipe.objects.filter(categories__in=self.object.categories.all(), visibility=1, status=1)[:10]
        if context['recs_recipes'].count() < 10:
            additional_items = Recipe.objects.filter(visibility=1, status=1).exclude(categories__in=self.object.categories.all())[:10-context['recs_recipes'].count()]
            context['recs_recipes'] = context['recs_recipes'] | additional_items
        if context['recs_recipes'].count() < 4:
            context['recs_recipes'] = None

        if user.is_authenticated and self.object.reviews.filter(author=user).exists():
            context["user_review_exists"] = 1
            context["user_review_rating"] = self.object.reviews.get(author=user).rating
        else:
            context["user_review_exists"] = 0

        return context



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

