from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import DetailView, ListView, TemplateView
from docs.source.conf import author

from additions.views import Status, Visibility, get_recs_news, get_news_PUBLISHED_ALL_SUBS, get_news_comments
from categories.models import CategoryGroup, RecipeCategory
from news.forms import CreateNewsCommentForm, CreateNewsForm
from news.models import News, NewsComment, NewsReview
from recipes.models import Recipe
from recipes.views import get_recs_recipes
from users.views import (_prepare_articles_data, validate_image_extension)

paginate_by = 32

class NewsView(ListView):
    template_name = "news/articles.html"
    model = News
    paginate_by = paginate_by

    def get_queryset(self):
        user = self.request.user
        queryset = get_news_PUBLISHED_ALL_SUBS(user)
        if (self.kwargs.get("slug", None)):
            category_obj = RecipeCategory.objects.get(slug=self.kwargs["slug"])
            queryset = queryset.filter(categories=category_obj)
        return queryset.order_by("-published_date")

    def get_context_data(self, **kwargs):
        context = super(NewsView, self).get_context_data(**kwargs)
        context['category_groups'] = CategoryGroup.objects.all()
        context['active_news'] = True
        context["kwargs"] = self.kwargs

        if (self.kwargs.get("slug", None)):
            context["kwargs"]["slug_name"] = RecipeCategory.objects.get(slug=self.kwargs["slug"]).name
        return context

class CreateNewsView(TemplateView):
    template_name = "news/add_news.html"

def news_create_view(request):
    if request.method == "GET":
        form = CreateNewsForm()

        return render(request, 'news/add_news.html', {
            'form': form,
            'category_groups': CategoryGroup.objects.all(),
            'visibility_descriptions': Visibility.TypeAndDescr,
        })
    elif request.method == "POST":
        data = request.POST
        files = request.FILES


        title = data.get("title", "")
        description_card = data.get("description_card", "")
        content_start = data.get("content_start", "")
        content_middle = data.get("content_middle", "")
        content_end = data.get("content_end", "")

        categories = RecipeCategory.objects.filter(id__in=data.getlist("categories", [])[:10])

        status = data.get("status", Status.DRAFT)
        visibility = data.get("visibility", Visibility.ME)

        preview = files.get("preview", None)

        item_data = {
            "title": title,
            "preview": preview,
            "description_card": description_card,
            "content_start": content_start,
            "content_middle": content_middle,
            "content_end": content_end,
            "visibility": visibility,
            "status": status,
            "author": request.user,
        }

        item_object = News(**item_data)
        item_object.full_clean()  # Валидация модели
        item_object.save()

        item_object.categories.set(categories)

        if "save" in data:
            return JsonResponse({
                'answer': 'Статья успешно создана или изменёна',
                'url': reverse("news:edit", kwargs={'pk': item_object.id}),
                'redirect': True,
            })
        elif "publish" in data:
            return JsonResponse({
                'answer': 'Статья успешно создана или изменёна',
                'redirect': True,
                'url': reverse("users:profile")
            })
        else:
            return JsonResponse({
                'answer': 'Статья успешно создана или изменёна',
                'url': reverse("news:edit", kwargs={'pk': item_object.id}),
                'redirect': True,
            })

def news_edit_view(request, pk):
    if request.method == "GET":
        item_object = get_object_or_404(News, id=pk)
        form = CreateNewsForm(instance=item_object)

        context = {
            'object': item_object,
            'form': form,
            'category_groups': CategoryGroup.objects.all(),
            'visibility_descriptions': Visibility.TypeAndDescr,
        }

        return render(request, 'news/edit_news.html', context=context)
    elif request.method == "POST":
        data = request.POST
        files = request.FILES

        item_object = get_object_or_404(News, id=pk)

        # Данные рецепта
        title = data.get("title", "")
        description_card = data.get("description_card") if data.get("description_card") != "" else " "
        content_start = data.get("content_start", "")
        content_middle = data.get("content_middle", "")
        content_end = data.get("content_end", "")

        categories = RecipeCategory.objects.filter(id__in=data.getlist("categories", []))

        status = data.get("status", Status.MODERATION if "publish" in data else Status.DRAFT)
        visibility = data.get("visibility", Visibility.ME)

        preview_deleted = data.get("preview_deleted")
        new_image = files.get("preview")
        preview = item_object.preview

        if new_image:
            preview = new_image
        elif preview_deleted:
            preview = None

        item_data = {
            "title": title,
            "preview": preview,
            "description_card": description_card,
            "content_start": content_start,
            "content_middle": content_middle,
            "content_end": content_end,
            "visibility": visibility,
            "status": status,
            "author": request.user,
        }

        item_object = get_object_or_404(News, id=pk)
        item_object.__dict__.update(item_data)  # Обновляем атрибуты
        item_object.save()

        item_object.categories.set(categories)

        if "save" in data:
            return JsonResponse({
                'answer': 'Статья успешно создана или изменёна',
                'redirect': False,
            })
        elif "publish" in data:
            return JsonResponse({
                'answer': 'Статья успешно создана или изменёна',
                'redirect': True,
                'url': reverse("users:profile")
            })
        else:
            return JsonResponse({
                'answer': 'Статья успешно создана или изменёна',
                'url': reverse("news:edit", kwargs={'pk': item_object.id}),
                'redirect': True,
            })

class DetailNewsView(DetailView):
    template_name = "news/detail_news.html"
    model = News

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        user = self.request.user
        if self.object.author_id != user.id:
            if self.object.status == Status.MODERATION:
                self.template_name = "additions/error_moderator.html"
                return self.render_to_response(context)
            elif self.object.status in (Status.UNPUBLISHED, Status.DRAFT):
                return super().get(request, *args, **kwargs)
            else:
                self.object.views += 1
                self.object.save()

        if self.object.preview:
            request.meta_og_image = self.object.preview
        request.meta_title = self.object.title
        request.meta_description = self.object.description_card
        request.meta_og_title = self.object.title
        request.meta_og_description = self.object.description_card

        return super().get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(DetailNewsView, self).get_context_data(**kwargs)

        user = self.request.user

        if self.object.author_id != user.id:
            if self.object.status == Status.MODERATION:
                return context

            subs_check = True
            only_me_check = self.object.visibility == Visibility.ME
            if self.object.visibility == Visibility.SUBS:
                subs_check = user in self.object.author.subscribers.all()

            elif self.object.status in (Status.UNPUBLISHED, Status.DRAFT) or not subs_check or only_me_check:
                raise Http404

        object_categories = self.object.categories.all()

        context['category_groups'] = CategoryGroup.objects.all()
        context['news_side'] = get_news_PUBLISHED_ALL_SUBS(user).order_by("-published_date")[:10]

        context['recs_recipes'] = get_recs_recipes(user, object_categories, None, 10)

        context['recs_news'] = get_recs_news(user, object_categories, self.object.pk, 10)

        if user.is_authenticated and self.object.newsreview_set.filter(author=user).exists():
            context["user_review_exists"] = 1
            context["user_review_rating"] = self.object.newsreview_set.get(author=user).rating
        else:
            context["user_review_exists"] = 0

        comments = get_news_comments(self.object)
        paginator = Paginator(comments, 2)  # 20 комментариев на страницу
        page_number = 1
        page_obj = paginator.get_page(page_number)

        context["comments"] = page_obj
        context["create_comment_form"] = CreateNewsCommentForm()
        context["iso_published_date"] = self.object.published_date.isoformat()

        return context

def bluk_create_objects(request):
    original_obj = News.objects.last()
    duplicates = []
    for i in range(1, 30):
        original_obj.id = None
        duplicates += [original_obj]
    News.objects.bulk_create(duplicates)

    return HttpResponseRedirect(reverse('main'))

@require_POST
def change_status(request):
    item_id = request.POST.get("item_id")
    data_status = request.POST.get("data_status")
    action_status = request.POST.get("action_status")
    page = request.POST.get('page', 1)

    item = get_object_or_404(News, id=item_id)
    item.status = action_status
    item.save()

    data_statuses = data_status.split(",")

    return JsonResponse(_prepare_articles_data(request.user, data_statuses, page))


@require_POST
def change_rating(request):
    user = request.user
    if user.is_authenticated:
        new_rating = int(request.POST.get("new_rating"))
        item_id = request.POST.get("item_id")

        item = get_object_or_404(News, id=item_id)

        review = NewsReview.objects.filter(author=user, news=item)
        if review.exists():
            review = review.first()
            review.rating = new_rating
            review.save()
        else:
            review = NewsReview.objects.create(author=user, news=item, rating=new_rating)
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

        item = get_object_or_404(News, id=item_id)

        review = NewsReview.objects.filter(author=user, news=item)
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

    item = get_object_or_404(News, id=item_id)

    if data_parent_id:
        parent = NewsComment.objects.get(id=data_parent_id)
        comment = NewsComment.objects.create(text=text, parent=parent, author=request.user, news=item)
    else:
        image = request.FILES.get("image")
        if image:
            validate_image_extension(image)
            comment = NewsComment.objects.create(text=text, image=image, author=request.user, news=item)
        else:
            comment = NewsComment.objects.create(text=text, author=request.user, news=item)

    return JsonResponse({
        'answer': "Комментарий успешно создан",
    })

@require_POST
def delete_comment(request):
    comment_id = request.POST.get("comment_id")

    comment = NewsComment.objects.get(id=comment_id)

    comment.delete()

    return JsonResponse({
        'answer': "Комментарий успешно удалён",
    })

@require_POST
def comment_reaction_change(request):
    comment_id = request.POST.get("comment_id")
    reaction_type = request.POST.get("reaction_type")
    user = request.user

    comment = get_object_or_404(NewsComment, id=comment_id)

    response = dict()

    liked_news_comments_exists = user.liked_news_comments.filter(id=comment_id).exists()
    disliked_news_comments_exists = user.disliked_news_comments.filter(id=comment_id).exists()

    if user.is_authenticated:
        if reaction_type == 'like':
            if liked_news_comments_exists:
                user.liked_news_comments.remove(comment)
                comment.likes = max(0, comment.likes - 1)

                response["answer"] = "Комментарий удалён из понравившихся"
            else:
                user.liked_news_comments.add(comment)
                comment.likes += 1
                if disliked_news_comments_exists:
                    user.disliked_news_comments.remove(comment)
                    comment.dislikes = max(0, comment.dislikes - 1)

                response["answer"] = "Комментарий добавлен в понравившиеся"
        elif reaction_type == 'dislike':
            if disliked_news_comments_exists:
                user.disliked_news_comments.remove(comment)
                comment.dislikes = max(0, comment.dislikes - 1)

                response["answer"] = "Комментарий удалён из непонравившихся"
            else:
                user.disliked_news_comments.add(comment)
                comment.dislikes += 1
                if liked_news_comments_exists:
                    user.liked_news_comments.remove(comment)
                    comment.likes = max(0, comment.likes - 1)

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

    item = get_object_or_404(News, id=object_id)

    comments = NewsComment.objects.filter(news=item, parent=None).order_by('-published_date')

    paginator = Paginator(comments, 2)  # 20 комментариев на страницу
    page_obj = paginator.get_page(page)

    context = {
        'comments': page_obj,
        'object': item,  # Передаем объект рецепта, если он используется в шаблоне
        'object_type': "news",
        'request': request,
    }

    # Рендерим HTML для новых комментариев
    return render(request, 'news/includes/comments_partial.html', context)

@require_GET
def load_more_comments(request):
    object_id = request.GET.get('object_id')
    page = request.GET.get('page')

    item = get_object_or_404(News, id=object_id)

    comments = NewsComment.objects.filter(news=item, parent=None).order_by('-published_date')

    paginator = Paginator(comments, 2)  # 20 комментариев на страницу
    page_obj = paginator.get_page(page)

    # Добавляем CSRF-токен в контекст
    context = {
        'comments': page_obj,
        'object': item,  # Передаем объект рецепта, если он используется в шаблоне
        'object_type': "news",
        'request': request,
    }
    context.update(csrf(request))  # Добавляем CSRF-токен

    # Рендерим HTML для новых комментариев
    comments_html = render_to_string('news/includes/comments_partial.html', context)

    return JsonResponse({
        'comments_html': comments_html,
        'has_next': page_obj.has_next(),
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
    })