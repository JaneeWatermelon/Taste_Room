from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import (Achievement, CategoryAchievement, Color,
                          GeneralAchievementCondition, User)


@admin.register(User)
class UserAdmin(BaseUserAdmin, admin.ModelAdmin):
    # form = UserChangeForm
    # add_form = UserCreationForm
    # change_password_form = AdminPasswordChangeForm

    list_display = ["username", "email", "date_joined"]

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': (
                    ('name', 'avatar', 'background_color'),
                    ('description_profile', 'description_recipe', 'description_news'),
                    'socials',
                    ('liked_recipes', 'liked_recipe_comments', 'disliked_recipe_comments',),
                    ('liked_news_comments', 'disliked_news_comments',),
                    ('subscribers', 'subscriptions'),
                    ('choosed_achiv', 'achivs'),
                )
            }
        ),
    )

    fieldsets = UserAdmin.fieldsets + (
        (None, {
            'fields': (
                    ('name', 'avatar', 'background_color'),
                    ('description_profile', 'description_recipe', 'description_news'),
                    'socials',
                    ('liked_recipes', 'liked_recipe_comments', 'disliked_recipe_comments',),
                    ('liked_news_comments', 'disliked_news_comments',),
                    ('subscribers', 'subscriptions'),
                    ('choosed_achiv', 'achivs'),
                )
            }
        ),
    )

@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "condition_general", "condition_self", "level",]

@admin.register(CategoryAchievement)
class CategoryAchievementAdmin(admin.ModelAdmin):
    pass

@admin.register(GeneralAchievementCondition)
class GeneralAchievementConditionAdmin(admin.ModelAdmin):
    pass

@admin.register(Color)
class ColorAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ["title", "hash", "sort_order"]
    list_editable = ["sort_order"]