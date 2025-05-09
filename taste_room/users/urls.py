from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from users.views import (AuthorPageView, ProfileView, change_back_fon,
                         change_profile_current_achiv, change_profile_image,
                         continue_reset_password, final_change_password,
                         get_search_subs, load_my_articles, load_my_recipes,
                         send_email_code, sub_unsub, user_login, user_logout,
                         user_registration)

app_name = "users"

urlpatterns = [
    path('profile', ProfileView.as_view(), name="profile"),
    path('author/<slug:username>', AuthorPageView.as_view(), name="author"),

    path('logout', user_logout, name="logout"),

    path('ajax/load_my_recipes', load_my_recipes, name="load_my_recipes_ajax"),
    path('ajax/load_my_articles', load_my_articles, name="load_my_articles_ajax"),

    path('ajax/sub_unsub', sub_unsub, name="sub_unsub_ajax"),
    path('ajax/get_search_subs', get_search_subs, name="get_search_subs_ajax"),

    path('ajax/change_back_fon', change_back_fon, name="change_back_fon_ajax"),
    path('ajax/change_profile_image', change_profile_image, name="change_profile_image_ajax"),
    path('ajax/change_profile_current_achiv', change_profile_current_achiv, name="change_profile_current_achiv_ajax"),

    path('ajax/user_registration', user_registration, name="user_registration_ajax"),
    path('ajax/user_login', user_login, name="user_login_ajax"),
    path('ajax/send_email_code', send_email_code, name="send_email_code_ajax"),
    path('ajax/continue_reset_password', continue_reset_password, name="continue_reset_password_ajax"),
    path('ajax/final_change_password', final_change_password, name="final_change_password_ajax"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
