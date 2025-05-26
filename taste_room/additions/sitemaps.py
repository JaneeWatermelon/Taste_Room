from django.contrib.sitemaps import Sitemap
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now

from additions.views import Visibility, Status
from news.models import News
from recipes.models import Recipe, RecipeCategory
from django.conf import settings

from users.models import User


class StaticSitemap(Sitemap):
    changefreq = "daily"  # Как часто обновляется (always, hourly, daily, weekly, monthly, yearly, never)
    priority = 0.7  # Приоритет (0.1 - 1.0)

    def items(self):
        reverses = [
            "recipes:index",
            "recipes:popular",
            "recipes:create",
            "news:index",
            "news:create",
            "users:profile",
        ]
        return reverses

    def location(self, item):
        return reverse(item)

    def lastmod(self, obj):
        return now().date()

class RecipesSitemap(Sitemap):
    changefreq = "daily"  # Как часто обновляется (always, hourly, daily, weekly, monthly, yearly, never)
    priority = 0.9  # Приоритет (0.1 - 1.0)

    def items(self):
        queryset = Recipe.objects.filter(
            Q(visibility=Visibility.ALL, status=Status.PUBLISHED)
        )
        return queryset

    def location(self, item):
        return reverse(f"recipes:detail", kwargs={"pk": item.pk, "slug": item.slug,})

    def lastmod(self, obj):
        return now().date()

    def get_urls(self, **kwargs):
        urls = super().get_urls(**kwargs)

        # Дополнительные URL для каждого рецепта
        for item in self.items():
            absolute_url = f"{settings.DOMAIN_NAME}{reverse('recipes:edit', kwargs={'pk': item.pk})}"
            new_priority = str(self.priority-0.1)
            new_priority.replace(',', '.')
            urls.append({
                'location': absolute_url,
                'lastmod': self.lastmod(item),
                'changefreq': self.changefreq,  # Реже, чем основная страница
                'priority': new_priority,  # Ниже приоритет
            })
        return urls

class NewsSitemap(Sitemap):
    changefreq = "daily"  # Как часто обновляется (always, hourly, daily, weekly, monthly, yearly, never)
    priority = 0.9  # Приоритет (0.1 - 1.0)

    def items(self):
        queryset = News.objects.filter(
            Q(visibility=Visibility.ALL, status=Status.PUBLISHED)
        )
        return queryset

    def location(self, item):
        return reverse(f"news:detail", kwargs={"pk": item.pk, "slug": item.slug,})

    def lastmod(self, obj):
        return now().date()

    def get_urls(self, **kwargs):
        urls = super().get_urls(**kwargs)

        # Дополнительные URL для каждого рецепта
        for item in self.items():
            absolute_url = f"{settings.DOMAIN_NAME}{reverse('news:edit', kwargs={'pk': item.pk})}"
            new_priority = str(self.priority - 0.1)
            new_priority.replace(',', '.')
            urls.append({
                'location': absolute_url,
                'lastmod': self.lastmod(item),
                'changefreq': self.changefreq,  # Реже, чем основная страница
                'priority': new_priority,  # Ниже приоритет
            })
        return urls

class UsersSitemap(Sitemap):
    changefreq = "daily"  # Как часто обновляется (always, hourly, daily, weekly, monthly, yearly, never)
    priority = 0.8  # Приоритет (0.1 - 1.0)

    def items(self):
        queryset = User.objects.all()
        return queryset

    def location(self, item):
        return reverse(f"users:author", kwargs={"username": item.username,})

    def lastmod(self, obj):
        return now().date()

class CategoriesSitemap(Sitemap):
    changefreq = "weekly"  # Как часто обновляется (always, hourly, daily, weekly, monthly, yearly, never)
    priority = 0.7  # Приоритет (0.1 - 1.0)

    def items(self):
        queryset = RecipeCategory.objects.all()
        return queryset

    def location(self, item):
        return reverse(f"recipes:category", kwargs={"slug": item.slug,})

    def lastmod(self, obj):
        return now().date()

    def get_urls(self, **kwargs):
        urls = super().get_urls(**kwargs)

        # Дополнительные URL для каждого рецепта
        for item in self.items():
            absolute_url = f"{settings.DOMAIN_NAME}{reverse('news:category', kwargs={'slug': item.slug})}"
            new_priority = str(self.priority)
            new_priority.replace(',', '.')
            urls.append({
                'location': absolute_url,
                'lastmod': self.lastmod(item),
                'changefreq': self.changefreq,  # Реже, чем основная страница
                'priority': new_priority,  # Ниже приоритет
            })
        return urls