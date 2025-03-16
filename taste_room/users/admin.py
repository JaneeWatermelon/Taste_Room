from django.contrib import admin
from unfold.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin

from django.contrib.auth.models import Group

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from users.models import User, Achievement, CategoryAchievement, Comment, GeneralAchievementCondition, Review

admin.site.unregister(Group)

admin.site.register(CategoryAchievement)
admin.site.register(GeneralAchievementCondition)

@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    list_display = ["username", "email", "date_joined"]

    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {
            'fields': (
                    ('name', 'avatar', 'background_color'),
                    ('description_profile', 'description_recipe', 'description_news'),
                    'socials',
                    ('liked_recipes_id', 'liked_comments_id', 'disliked_comments_id',),
                    ('subscribers_id', 'subscriptions_id'),
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
                    ('liked_recipes_id', 'liked_comments_id', 'disliked_comments_id',),
                    ('subscribers_id', 'subscriptions_id'),
                    ('choosed_achiv', 'achivs'),
                )
            }
        ),
    )

@admin.register(Achievement)
class AchievementAdmin(ModelAdmin):
    list_display = ["title", "category", "condition_general", "condition_self", "level",]

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ["author", "likes", "dislikes", "parent", "published_date",]

@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ["author", "rating",]

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
