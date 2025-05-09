from decimal import Decimal

from django.core.paginator import Paginator
from django.db.models import Count, Q, prefetch_related_objects, F
from django.db.models.functions import Lower
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify
from django.utils.timezone import now, timedelta
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, UpdateView)

from additions.views import (Status, Visibility,
                             transliterate_russian_to_pseudo_english, get_recipes_PUBLISHED_ALL_SUBS, get_recs_recipes,
                             get_recipes_related)
from categories.models import CategoryGroup, RecipeCategory
from news.views import get_news_PUBLISHED_ALL_SUBS, get_recs_news
from recipes.forms import (CreateRecipeCommentForm, CreateRecipeForm)
from recipes.models import (Difficulty, Ingredient, Recipe, RecipeComment,
                            RecipeIngredient, RecipePreview, RecipeReview,
                            RecipeStep, Scipy, Units)
from users.views import _prepare_recipes_data, validate_image_extension


def DHMS(initial_days=0, initial_hours=0, initial_minutes=0, initial_seconds=0):  # Days Hours Minutes Seconds
    total_seconds = initial_days * 86400 + initial_hours * 3600 + initial_minutes * 60 + initial_seconds
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return {
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
    }

paginate_by = 32
support_paginate_by = 24

class MainView(TemplateView):
    template_name = "recipes/main.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(MainView, self).get_context_data(**kwargs)
        context['ingredients'] = Ingredient.objects.order_by("-popularity")[:6]
        all_recipes = get_recipes_PUBLISHED_ALL_SUBS(user)
        context['recipes'] = all_recipes.order_by("-published_date")[:paginate_by]
        context['recipes_popular'] = all_recipes.order_by('-popularity')[:paginate_by]

        context['recipes_1'] = context['recipes'][:support_paginate_by]
        context['recipes_2'] = context['recipes'][support_paginate_by:]
        context['recipes_popular_1'] = context['recipes_popular'][:support_paginate_by]
        context['recipes_popular_2'] = context['recipes_popular'][support_paginate_by:]

        context['articles'] = get_news_PUBLISHED_ALL_SUBS(user)[:10]

        return context

class CategoryRecipesView(ListView):
    template_name = "recipes/category_recipes.html"
    model = Recipe
    paginate_by = paginate_by

    def get_queryset(self):
        user = self.request.user
        queryset = get_recipes_PUBLISHED_ALL_SUBS(user)
        if (self.kwargs.get("slug", None)):
            category_obj = RecipeCategory.objects.get(slug=self.kwargs["slug"])
            queryset = queryset.filter(categories=category_obj)
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

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        ingredients_ids = self.request.GET.get("ingredients_ids")
        if ingredients_ids:
            ingredients_ids = ingredients_ids.split(",")
            Ingredient.objects.filter(id__in=ingredients_ids).update(popularity=F("popularity")+1)
        return self.render_to_response(context)

    def get_queryset(self):
        user = self.request.user
        q_param = self.request.GET.get("q")
        ingredients_ids = self.request.GET.get("ingredients_ids")

        if q_param:
            by_title = find_similar_recipes(q_param, user).distinct()
            by_icontains = word_search_recipes(q_param, user).distinct()

            queryset = get_recipes_related((by_title | by_icontains).distinct())
        elif ingredients_ids:
            # Аннотируем количеством совпавших ингредиентов
            ingredients_ids = ingredients_ids.split(",")
            recipes = Recipe.objects.annotate(
                match_count=Count('recipeingredient__ingredient',
                                  filter=Q(recipeingredient__ingredient__id__in=ingredients_ids)
                                  )
            )

            # Сортируем по убыванию совпадений и другим критериям (например, рейтингу)
            queryset = get_recipes_related(recipes).order_by('-match_count', '-popularity', '-rating')
        else:
            queryset = super(SearchRecipesView, self).get_queryset()
        return queryset

    def get_context_data(self, **kwargs):
        context = super(SearchRecipesView, self).get_context_data(**kwargs)

        q_param = self.request.GET.get("q")
        ingredients_ids = self.request.GET.get("ingredients_ids")

        context['category_groups'] = CategoryGroup.objects.all()
        if q_param:
            context['prompt_type'] = "q"
            context['prompt_params'] = q_param
            context['prompt'] = q_param
        elif ingredients_ids:
            context['prompt_type'] = "ingredients_ids"
            context['prompt_params'] = ingredients_ids
            ingredients_titles = []
            for ingredient in Ingredient.objects.filter(id__in=ingredients_ids.split(",")):
                ingredients_titles += [ingredient.title]
            context['prompt'] = ", ".join(ingredients_titles)
        else:
            context['prompt'] = ""

        return context

class PopularRecipesView(ListView):
    template_name = "recipes/popular_recipes.html"
    model = Recipe
    paginate_by = paginate_by

    def get_queryset(self):
        user = self.request.user
        queryset = get_recipes_PUBLISHED_ALL_SUBS(user).order_by('-popularity')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(PopularRecipesView, self).get_context_data(**kwargs)

        context['recipes_popular_1'] = context["object_list"][:24]
        context['recipes_popular_2'] = context["object_list"][24:]
        context['active_popular'] = True

        return context

def recipe_create_view(request):
    if request.method == "GET":
        form = CreateRecipeForm()

        return render(request, 'recipes/add_recipe.html', {
            'form': form,
            'category_groups': CategoryGroup.objects.all(),
            'visibility_descriptions': Visibility.TypeAndDescr,
        })
    elif request.method == "POST":
        data = request.POST
        files = request.FILES

        # Данные рецепта
        title = data.get("title", "")
        description_inner = " "
        description_card = " "

        categories = RecipeCategory.objects.filter(id__in=data.getlist("categories", [])[:10])

        difficulty = int(data.get("difficulty", Difficulty.NEWBIE))
        scipy = int(data.get("scipy", Scipy.NEWBIE))

        status = data.get("status", Status.DRAFT)
        visibility = data.get("visibility", Visibility.ME)
        portions = 1

        dhms_general = DHMS(
            initial_days=int(data.get("days_general", 0)),
            initial_hours=int(data.get("hours_general", 0)),
            initial_minutes=int(data.get("minutes_general", 0)),
        )
        cook_time_full = timedelta(days=dhms_general["days"], hours=dhms_general["hours"],
                                   minutes=dhms_general["minutes"])

        dhms_active = DHMS(
            initial_days=int(data.get("days_active", 0)),
            initial_hours=int(data.get("hours_active", 0)),
            initial_minutes=int(data.get("seconds_active", 0)),
        )
        cook_time_active = timedelta(days=dhms_active["days"], hours=dhms_active["hours"],
                                     minutes=dhms_active["minutes"])

        video_url_first = data.get("video_url_first", "")
        video_url_second = data.get("video_url_second", "")

        previews_data = {}
        for i in range(1, 4):
            image_key = f"preview_{i}"
            previews_data[image_key] = files.get(image_key, None)

        previews = RecipePreview.objects.create(**previews_data)

        recipe_data = {
            "title": title,
            "previews": previews,
            "description_inner": description_inner,
            "description_card": description_card,
            "video_url_first": video_url_first,
            "video_url_second": video_url_second,
            "cook_time_full": cook_time_full,
            "cook_time_active": cook_time_active,
            "scipy": scipy,
            "difficulty": difficulty,
            "visibility": visibility,
            "portions": portions,
            "status": status,
            "author": request.user,
        }

        print(data)
        print(recipe_data)

        recipe = Recipe(**recipe_data)
        recipe.full_clean()  # Валидация модели
        recipe.save()

        recipe.categories.set(categories)

        for i in range(1, 21):
            step_image = files.get(f"step_image_{i}")
            if step_image:
                step_text = data.get(f"text_{i}")
                RecipeStep.objects.create(recipe=recipe, image=step_image, text=step_text)

        for i in range(1, int(data.get("ingredients_count", 25)) + 1):
            ingredient_id = data.get(f"ingredient_id_{i}")
            if ingredient_id:
                ingredient = get_object_or_404(Ingredient, id=ingredient_id)
                ingredient_count = int(data.get(f"ingredient_count_{i}", 0))
                ingredient_measurement = data.get(f"ingredient_measurement_{i}", "гр")
                ingredient_checkbox = data.get(f"ingredient_checkbox_{i}")
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    quantity=ingredient_count,
                    unit=ingredient_measurement,
                    can_exclude=ingredient_checkbox,
                )

        return JsonResponse({
            'redirect': True,
            'url': reverse("recipes:edit", kwargs={'pk': recipe.id})
        })

def recipe_edit_view(request, pk):
    if request.method == "GET":
        recipe = get_object_or_404(Recipe, id=pk)
        form = CreateRecipeForm(instance=recipe)

        context = {
            'object': recipe,
            'form': form,
            'steps': recipe,
            'category_groups': CategoryGroup.objects.all(),
            'visibility_descriptions': Visibility.TypeAndDescr,
            'units_choices': Units.List,
        }

        return render(request, 'recipes/edit_recipe.html', context=context)
    elif request.method == "POST":
        data = request.POST
        files = request.FILES

        recipe = get_object_or_404(Recipe, id=pk)

        # Данные рецепта
        title = data.get("title", "")
        description_inner = data.get("description_inner") if data.get("description_inner") != "" else " "
        description_card = data.get("description_card") if data.get("description_card") != "" else " "

        categories = RecipeCategory.objects.filter(id__in=data.getlist("categories", []))

        difficulty = int(data.get("difficulty", Difficulty.NEWBIE))
        scipy = int(data.get("scipy", Scipy.NEWBIE))

        status = data.get("status", Status.MODERATION if "publish" in data else Status.DRAFT)
        visibility = data.get("visibility", Visibility.ME)
        portions = int(data.get("portions")) if data.get("portions").isdigit() else 1

        dhms_general = DHMS(
            initial_days = int(data.get("days_general", 0)),
            initial_hours = int(data.get("hours_general", 0)),
            initial_minutes = int(data.get("minutes_general", 0)),
        )
        cook_time_full = timedelta(days=dhms_general["days"], hours=dhms_general["hours"],
                                   minutes=dhms_general["minutes"])

        dhms_active = DHMS(
            initial_days=int(data.get("days_active", 0)),
            initial_hours=int(data.get("hours_active", 0)),
            initial_minutes=int(data.get("seconds_active", 0)),
        )
        cook_time_active = timedelta(days=dhms_active["days"], hours=dhms_active["hours"],
                                   minutes=dhms_active["minutes"])

        video_url_first = data.get("video_url_first", "")
        video_url_second = data.get("video_url_second", "")

        existing_previews = [recipe.previews.preview_1, recipe.previews.preview_2, recipe.previews.preview_3]
        for i in range(1, 4):
            field_name = f"preview_{i}"
            new_image = files.get(field_name)
            existing_image_position = data.get(f"existing_preview_position_{i}")

            if new_image:
                setattr(recipe.previews, field_name, new_image)
            elif existing_image_position:
                existing_image_index = int(existing_image_position) - 1
                setattr(recipe.previews, field_name, existing_previews[existing_image_index])
            else:
                setattr(recipe.previews, field_name, None)

        recipe.previews.save()

        recipe_data = {
            "title": title,
            "previews": recipe.previews,
            "description_inner": description_inner,
            "description_card": description_card,
            "video_url_first": video_url_first,
            "video_url_second": video_url_second,
            "cook_time_full": cook_time_full,
            "cook_time_active": cook_time_active,
            "scipy": scipy,
            "difficulty": difficulty,
            "visibility": visibility,
            "portions": portions,
            "status": status,
            "author": request.user,
        }

        recipe = get_object_or_404(Recipe, id=pk)
        recipe.__dict__.update(recipe_data)  # Обновляем атрибуты
        recipe.save()


        recipe.categories.set(categories)

        new_step_ids = dict()

        for i in range(1, 21):
            new_image = files.get(f"step_image_{i}")
            existing_image_name = data.get(f"existing_step_image_name_{i}")

            step_id = data.get(f"step_id_{i}")
            step_text = data.get(f"text_{i}")

            if new_image:
                if step_id:
                    step = RecipeStep.objects.get(id=step_id)

                    # Удаляем старое изображение, если оно есть
                    if step.image:
                        step.image.delete(save=False)

                    step.image = new_image
                    step.text = step_text
                    step.sort_order = i
                    step.save()
                else:
                    new_step = RecipeStep.objects.create(recipe=recipe, image=new_image, text=step_text, sort_order=i)
                    new_step_ids[f"step_id_{i}"] = new_step.id
            elif existing_image_name:
                RecipeStep.objects.filter(id=step_id).update(text=step_text, sort_order=i)
            else:
                pass

        delete_step_ids = data.get(f"delete_step_ids")
        for step_id in delete_step_ids.split(','):
            try:
                step = get_object_or_404(RecipeStep, id=step_id)
                step.delete()
            except:
                pass

        for i in range(1, int(data.get("ingredients_count", 25)) + 1):
            ingredient_id = data.get(f"ingredient_id_{i}")
            recipe_ingredient_id = data.get(f"recipe_ingredient_id_{i}")

            ingredient_count = int(data.get(f"ingredient_count_{i}", 0))
            ingredient_measurement = data.get(f"ingredient_measurement_{i}", "гр")
            ingredient_checkbox = True if data.get(f"ingredient_checkbox_{i}") else False

            if ingredient_id:
                ingredient = get_object_or_404(Ingredient, id=ingredient_id)
                if recipe_ingredient_id:
                    RecipeIngredient.objects.filter(id=recipe_ingredient_id).update(
                        quantity=ingredient_count,
                        unit=ingredient_measurement,
                        can_exclude=ingredient_checkbox,
                    )
                else:
                    RecipeIngredient.objects.create(
                        recipe=recipe,
                        ingredient=ingredient,
                        quantity=ingredient_count,
                        unit=ingredient_measurement,
                        can_exclude=ingredient_checkbox,
                    )

        delete_recipe_ingredient_ids = data.get(f"delete_recipe_ingredient_ids")
        for ingredient_id in delete_recipe_ingredient_ids.split(','):
            try:
                print(ingredient_id)
                recipe_ingredient = get_object_or_404(RecipeIngredient, id=ingredient_id)
                print(recipe_ingredient)
                recipe_ingredient.delete()
            except:
                pass

        if "save" in data:
            return JsonResponse({
                'answer': 'Рецепт успешно создан или изменён',
                'new_step_ids': new_step_ids,
                'redirect': False,
            })
        elif "publish" in data:
            return JsonResponse({
                'answer': 'Рецепт успешно создан или изменён',
                'redirect': True,
                'url': reverse("users:profile")
            })
        else:
            return JsonResponse({
                'answer': 'Рецепт успешно создан или изменён',
                'new_step_ids': new_step_ids,
                'redirect': False,
            })


@require_GET
def add_recipe_step(request):
    next_item_number = request.GET.get("next_item_number", "100")

    if int(next_item_number) <= 20:
        context = {
            'steps': [1],
            'next_item_number': next_item_number,
        }

        html_data = render_to_string("recipes/includes/preview_step_item.html", context=context)

        return JsonResponse({
            "html_data": html_data,
        })
    else:
        return JsonResponse({
            "overflow": True,
        })

@require_GET
def add_ready_photo(request):
    next_item_number = request.GET.get("next_item_number", "100")

    if int(next_item_number) <= 3:
        context = {
            'ready_photos': [1],
            'next_item_number': next_item_number,
        }

        html_data = render_to_string("recipes/includes/ready_photo_item.html", context=context)

        return JsonResponse({
            "html_data": html_data,
        })
    else:
        return JsonResponse({
            "overflow": True,
        })

class DetailRecipeView(DetailView):
    template_name = "recipes/detail_recipe.html"
    model = Recipe

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        user = self.request.user


        if self.object.author != user:
            if self.object.status == Status.MODERATION:
                return context

            subs_check = True
            only_me_check = self.object.visibility == Visibility.ME
            print(only_me_check)
            if self.object.visibility == Visibility.SUBS:
                subs_check = user in self.object.author.subscribers.all()

            elif self.object.status in (Status.UNPUBLISHED, Status.DRAFT) or not subs_check or only_me_check:
                raise Http404

        context['category_groups'] = CategoryGroup.objects.prefetch_related("categories", "categories__children")

        context['recipe_calories_per_100g'] = self.object.calculate_calories_per_100g()
        context['recipe_ingredients'] = self.object.recipeingredient_set.all()

        context['side_articles'] = get_news_PUBLISHED_ALL_SUBS(user).order_by("-published_date")[:10]

        recipe_categories = self.object.categories.all()

        context['recs_recipes'] = get_recs_recipes(user, recipe_categories, self.object.pk, 10)

        context['recs_news'] = get_recs_news(user, recipe_categories, None, 10)

        if user.is_authenticated and self.object.recipereview_set.filter(author=user).exists():
            context["user_review_exists"] = 1
            context["user_review_rating"] = self.object.recipereview_set.get(author=user).rating
        else:
            context["user_review_exists"] = 0

        comments = RecipeComment.objects.filter(recipe=self.object, parent=None).order_by('-published_date')
        paginator = Paginator(comments, 2)  # 20 комментариев на страницу
        page_number = 1
        page_obj = paginator.get_page(page_number)

        context["comments"] = page_obj
        context["create_comment_form"] = CreateRecipeCommentForm()
        context["ingredients_list"] = []
        for recipe_ingredient in context['recipe_ingredients']:
            context["ingredients_list"].append(recipe_ingredient.ingredient.title)
        context["ingredients_list"] = ",".join(context["ingredients_list"])

        return context

    def get(self, request, *args, **kwargs):
        self.object = Recipe.objects.filter(id=self.kwargs.get("pk")).select_related("previews", "author").prefetch_related("recipereview_set", "recipeingredient_set", "recipeingredient_set__ingredient",).get()
        context = self.get_context_data(object=self.object)

        if self.object.previews.preview_1:
            request.meta_og_image = self.object.previews.preview_1
        request.meta_title = self.object.title
        request.meta_description = self.object.description_card
        request.meta_og_title = self.object.title
        request.meta_og_description = self.object.description_card

        if self.object.status == Status.MODERATION:
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

@require_POST
def recipe_like_change(request):
    recipe_id = request.POST.get("recipe_id")
    user = request.user

    liked_recipes_exists = user.liked_recipes.filter(id=recipe_id).exists()
    liked_recipe = get_object_or_404(Recipe, id=recipe_id)

    if user.is_authenticated:
        if liked_recipes_exists:
            user.liked_recipes.remove(liked_recipe)
            user.save()
            return JsonResponse({"answer": "Рецепт удалён из понравившихся"})
        else:
            user.liked_recipes.add(liked_recipe)
            user.save()
            return JsonResponse({"answer": "Рецепт добавлен в понравившиеся"})
    else:
        return JsonResponse({"answer": "Пользователь не авторизован"})

@require_POST
def change_recipe_ingredients(request):
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


def find_similar_recipes(search_prompt, user, threshold=10):
    all_recipes = get_recipes_PUBLISHED_ALL_SUBS(user)
    similar_ids = []
    search_prompt = search_prompt.lower().replace("ё", "е")

    for recipe in all_recipes:
        my_treshold = distance(search_prompt, recipe.title.lower().replace("ё", "е"))
        if my_treshold <= threshold:
            similar_ids.append(recipe.id)

    return Recipe.objects.filter(id__in=similar_ids)

def word_search_recipes(search_prompt, user):
    # 2. Поиск по словам
    words = search_prompt.split()
    word_q = Q()
    for word in words:
        word = word.lower()
        word_q |= Q(title__icontains=word) | Q(description_card__icontains=word) | Q(recipeingredient__ingredient__title__icontains=word)
    word_results = get_recipes_PUBLISHED_ALL_SUBS(user).filter(word_q)

    return word_results

@require_POST
def change_status(request):
    item_id = request.POST.get("item_id")
    data_status = request.POST.get("data_status")
    action_status = request.POST.get("action_status")
    page = request.POST.get('page', 1)

    item = get_object_or_404(Recipe, id=item_id)
    item.status = action_status
    item.save()

    data_statuses = data_status.split(",")

    return JsonResponse(_prepare_recipes_data(request.user, data_statuses, page))


@require_POST
def change_rating(request):
    user = request.user
    if user.is_authenticated:
        new_rating = int(request.POST.get("new_rating"))
        item_id = request.POST.get("item_id")

        item = get_object_or_404(Recipe, id=item_id)

        review = RecipeReview.objects.filter(author=user, recipe=item)
        if review.exists():
            review = review.first()
            review.rating = new_rating
            review.save()
        else:
            review = RecipeReview.objects.create(author=user, recipe=item, rating=new_rating)
        return JsonResponse({
            "answer": "Отзыв успешно создан или изменён"
        })
    else:
        return JsonResponse({
            "answer": "Пользователь не авторизован"
        })

@require_POST
def delete_rating(request):
    user = request.user
    if user.is_authenticated:
        item_id = request.POST.get("item_id")

        item = get_object_or_404(Recipe, id=item_id)

        review = RecipeReview.objects.filter(author=user, recipe=item)
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


@require_POST
def create_comment(request):
    item_id = request.POST.get("item_id")

    text = request.POST.get("text")
    data_parent_id = request.POST.get("data_parent_id")

    item = Recipe.objects.get(id=item_id)

    if data_parent_id:
        parent = RecipeComment.objects.get(id=data_parent_id)
        comment = RecipeComment.objects.create(text=text, parent=parent, author=request.user, recipe=item)
    else:
        image = request.FILES.get("image")
        if image:
            validate_image_extension(image)
            comment = RecipeComment.objects.create(text=text, image=image, author=request.user, recipe=item)
        else:
            comment = RecipeComment.objects.create(text=text, author=request.user, recipe=item)

    return JsonResponse({
        'answer': "Комментарий успешно создан",
    })

@require_POST
def delete_comment(request):
    comment_id = request.POST.get("comment_id")

    comment = RecipeComment.objects.get(id=comment_id)

    comment.delete()

    return JsonResponse({
        'answer': "Комментарий успешно удалён",
    })

@require_POST
def comment_reaction_change(request):
    comment_id = request.POST.get("comment_id")
    reaction_type = request.POST.get("reaction_type")
    user = request.user

    comment = get_object_or_404(RecipeComment, id=comment_id)

    response = dict()

    liked_recipe_comments_exists = user.liked_recipe_comments.filter(id=comment_id).exists()
    disliked_recipe_comments_exists = user.disliked_recipe_comments.filter(id=comment_id).exists()

    if user.is_authenticated:
        if reaction_type == 'like':
            if liked_recipe_comments_exists:
                user.liked_recipe_comments.remove(comment)
                comment.likes = max(0, comment.likes-1)

                response["answer"] = "Комментарий удалён из понравившихся"
            else:
                user.liked_recipe_comments.add(comment)
                comment.likes += 1
                if disliked_recipe_comments_exists:
                    user.disliked_recipe_comments.remove(comment)
                    comment.dislikes = max(0, comment.dislikes-1)

                response["answer"] = "Комментарий добавлен в понравившиеся"
        elif reaction_type == 'dislike':
            if disliked_recipe_comments_exists:
                user.disliked_recipe_comments.remove(comment)
                comment.dislikes = max(0, comment.dislikes-1)

                response["answer"] = "Комментарий удалён из непонравившихся"
            else:
                user.disliked_recipe_comments.add(comment)
                comment.dislikes += 1
                if liked_recipe_comments_exists:
                    user.liked_recipe_comments.remove(comment)
                    comment.likes = max(0, comment.likes-1)

                response["answer"] = "Комментарий добавлен в непонравившиеся"

        user.save()
        comment.save()
        return JsonResponse(response)
    else:
        return JsonResponse({"answer": "Пользователь не авторизован"})

@require_GET
def comments_partial_view(request):
    object_id = request.GET.get('object_id')
    page = request.GET.get('page')

    item = get_object_or_404(Recipe, id=object_id)

    comments = RecipeComment.objects.filter(recipe=item, parent=None).order_by('-published_date')

    paginator = Paginator(comments, 2)  # 20 комментариев на страницу
    page_obj = paginator.get_page(page)

    context = {
        'comments': page_obj,
        'object': item,  # Передаем объект рецепта, если он используется в шаблоне
        'object_type': "recipe",  # Передаем объект рецепта, если он используется в шаблоне
        'request': request,
    }

    # Рендерим HTML для новых комментариев
    return render(request, 'recipes/includes/comments_partial.html', context)

@require_GET
def load_more_comments(request):
    object_id = request.GET.get('object_id')
    page = request.GET.get('page')

    item = get_object_or_404(Recipe, id=object_id)

    comments = RecipeComment.objects.filter(recipe=item, parent=None).order_by('-published_date')

    paginator = Paginator(comments, 2)  # 20 комментариев на страницу
    page_obj = paginator.get_page(page)

    # Добавляем CSRF-токен в контекст
    context = {
        'comments': page_obj,
        'object': item,  # Передаем объект рецепта, если он используется в шаблоне
        'object_type': "recipe",  # Передаем объект рецепта, если он используется в шаблоне
        'request': request,  # Передаем объект рецепта, если он используется в шаблоне
    }
    context.update(csrf(request))  # Добавляем CSRF-токен

    # Рендерим HTML для новых комментариев
    comments_html = render_to_string('recipes/includes/comments_partial.html', context)

    return JsonResponse({
        'comments_html': comments_html,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    })

@require_GET
def ingredient_cards_autocomplete(request):
    search_term = request.GET.get('data_term', '').lower()  # Приводим к нижнему регистру
    active_ids_list = request.GET.getlist('active_ids_list')

    active_ids_list = list(map(int, active_ids_list))

    if search_term != '':
        search_term = slugify(transliterate_russian_to_pseudo_english(search_term))

        ingredients = Ingredient.objects.filter(slug__icontains=search_term)[:6]
        html_data = render_to_string("recipes/includes/ingredient_card_items.html", context={
            "ingredients": ingredients,
            "active_ids_list": active_ids_list,
        })
        return JsonResponse({
            "html_data": html_data,
        })
    else:
        return JsonResponse({
            "answer": "Пустой список ингредиентов",
        }, 404)

@require_GET
def add_ingredient_card_item(request):
    data_id = request.GET.get('data_id')
    if data_id:
        ingredient = get_object_or_404(Ingredient, id=data_id)

        context = {
            'ingredients': [ingredient],
        }

        html_data = render_to_string("recipes/includes/ingredient_card_items.html", context=context)

        return JsonResponse({
            "html_data": html_data,
        })
    else:
        return JsonResponse({
            "error": "Ингредиент не найден",
        }, 404)

@require_GET
def ingredient_autocomplete(request):
    search_term = request.GET.get('data_term', '').lower()  # Приводим к нижнему регистру

    if search_term != '':
        search_term = slugify(transliterate_russian_to_pseudo_english(search_term))

        ingredients = Ingredient.objects.filter(slug__icontains=search_term)[:10]
        results = [{'id': ing.id, 'value': ing.title} for ing in ingredients]
    else:
        results = []

    return JsonResponse({
        "ingredients_choices": results,
    })

@require_GET
def add_ingredient_item(request):
    data_id = request.GET.get('data_id', '')
    next_item_number = request.GET.get('next_item_number', '')
    if data_id:
        ingredient = get_object_or_404(Ingredient, id=data_id)

        context = {
            'ingredients': [ingredient],
            'next_item_number': next_item_number,
            'choices': Units.List,
        }

        html_data = render_to_string("recipes/includes/ingredient_item.html", context=context)

        return JsonResponse({
            "html_data": html_data,
        })
    else:
        return JsonResponse({
            "error": "Ингредиент не найден",
        }, 400)

