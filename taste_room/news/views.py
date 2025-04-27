from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST, require_GET
from django.views.generic import DetailView, ListView, TemplateView

from categories.models import CategoryGroup, RecipeCategory
from news.forms import CreateNewsCommentForm
from news.models import News, NewsComment, NewsReview
from recipes.models import Recipe
from users.views import (_prepare_articles_data, load_my_articles,
                         load_my_recipes, validate_image_extension)

paginate_by = 24


class NewsView(ListView):
    template_name = "news/articles.html"
    model = News
    paginate_by = paginate_by

    def get_queryset(self):
        queryset = super(NewsView, self).get_queryset().select_related("author").prefetch_related("newsreview_set")
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

        if self.object.status == 4:
            return context
        elif self.object.status in (2, 4):
            raise Http404
        else:
            object_categories = self.object.categories.all()

            context['category_groups'] = CategoryGroup.objects.all()
            context['news_side'] = News.objects.filter(visibility=1, status=1).select_related("author").prefetch_related("newsreview_set").order_by("-published_date")[:10]

            context['recs_recipes'] = Recipe.objects.filter(categories__in=object_categories, visibility=1, status=1).select_related("previews", "author")[:10]
            if context['recs_recipes'].count() < 10:
                additional_items = Recipe.objects.filter(visibility=1, status=1).exclude(categories__in=object_categories).select_related("previews", "author")[:10-context['recs_recipes'].count()]
                context['recs_recipes'] = context['recs_recipes'] | additional_items
            if context['recs_recipes'].count() < 4:
                context['recs_recipes'] = None

            context['recs_news'] = News.objects.filter(categories__in=object_categories, visibility=1, status=1).select_related("author").prefetch_related("newsreview_set")[:10]
            if context['recs_news'].count() < 10:
                additional_items = News.objects.filter(visibility=1, status=1).exclude(categories__in=object_categories).select_related("author").prefetch_related("newsreview_set")[:10-context['recs_news'].count()]
                context['recs_news'] = context['recs_news'] | additional_items
            if context['recs_news'].count() < 4:
                context['recs_news'] = None

            if user.is_authenticated and self.object.newsreview_set.filter(author=user).exists():
                context["user_review_exists"] = 1
                context["user_review_rating"] = self.object.newsreview_set.get(author=user).rating
            else:
                context["user_review_exists"] = 0

            comments = NewsComment.objects.filter(news=self.object, parent=None).order_by('-published_date')
            paginator = Paginator(comments, 2)  # 20 комментариев на страницу
            page_number = 1
            page_obj = paginator.get_page(page_number)

            context["comments"] = page_obj
            context["create_comment_form"] = CreateNewsCommentForm()

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

    return JsonResponse(_prepare_articles_data(request.user, data_status, page))


@require_POST
def change_rating(request):
    user = request.user
    if user.is_authenticated:
        new_rating = int(request.POST.get("new_rating"))
        item_id = request.POST.get("item_id")

        item = News.objects.get(id=item_id)

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

        item = News.objects.get(id=item_id)

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

    item = News.objects.get(id=item_id)

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