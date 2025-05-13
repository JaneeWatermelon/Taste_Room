import os
from pathlib import Path

import environ
from celery.schedules import crontab

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, False),
    REDIS_LOCATION=(str, False),

    DATABASES_NAME=(str, False),
    DATABASES_USER=(str, False),
    DATABASES_PASSWORD=(str, False),
    DATABASES_PORT=(str, False),

    EMAIL_HOST=(str, False),
    EMAIL_HOST_PASSWORD=(str, False),
    EMAIL_HOST_USER=(str, False),
    EMAIL_PORT=(int, False),
    EMAIL_USE_SSL=(bool, False),
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Take environment variables from .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ["127.0.0.1", "45.131.40.35", "tasteroom.ru"]

INTERNAL_IPS = [
    "127.0.0.1",
]


# Application definition

INSTALLED_APPS = [
    # "unfold",  # before django.contrib.admin
    # "unfold.contrib.filters",  # optional, if special filters are needed
    # "unfold.contrib.forms",  # optional, if special form elements are needed
    # "unfold.contrib.inlines",  # optional, if special inlines are needed
    # "unfold.contrib.import_export",  # optional, if django-import-export package is used
    # "unfold.contrib.guardian",  # optional, if django-guardian package is used
    # "unfold.contrib.simple_history",  # optional, if django-simple-history package is used

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'ckeditor',
    'ckeditor_uploader',
    'imagekit',
    'debug_toolbar',
    'rest_framework',
    'adminsortable2',

    'recipes',
    'additions',
    'categories',
    'news',
    'users',
    'arts',
    'api',

    'django_cleanup.apps.CleanupConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'additions.middleware.MetaTagsMiddleware',
]

ROOT_URLCONF = 'taste_room.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'users.context_processors.registration_form',
                'users.context_processors.login_form',
                'users.context_processors.change_password_form',
                'users.context_processors.user_liked_recipes',
                # 'users.context_processors.cache_timeout',
                'recipes.context_processors.empty_block',
            ],
        },
    },
]

WSGI_APPLICATION = 'taste_room.wsgi.application'


# Database

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DATABASES_NAME'),
        'USER': env('DATABASES_USER'),
        'PASSWORD': env('DATABASES_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': env('DATABASES_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# CKeditor
CKEDITOR_UPLOAD_PATH = "ckeditor/"

CKEDITOR_CONFIGS = {
    'awesome_ckeditor': {
        'toolbar': [
            ['Undo', 'Redo',
             '-', 'Bold', 'Italic', 'Underline', 'Strike',
             # 'Link',
             '-', 'Image',
             '-', 'Format',
             '-', 'NumberedList', 'BulletedList'
            ],

        ],
        'extraAllowedContent': 'h2 h3 h4 h5 h6',
        'disallowedContent': 'h1',
        'removeButtons': 'Heading',
        # 'width': '700px',

        'removeDialogTabs': 'link:upload;image:Link;image:advanced;image:target',
        'filebrowserUploadUrl': '/ckeditor/upload/',
        'filebrowserBrowseUrl': None,

        'image_previewText': ' ',
        'image_removeLinkByEmptyURL': True,
        'disableNativeSpellChecker': False,
    }
}

# redis
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env('REDIS_LOCATION'),
    }
}

# Celery
CELERY_BROKER_URL = env('REDIS_LOCATION')
CELERY_RESULT_BACKEND = env('REDIS_LOCATION')

CELERY_BEAT_SCHEDULE = {
    'check_recipe_moderation_every_10_min': {
        'task': 'recipes.tasks.check_moderation_status',
        'schedule': 600.0,
    },
    'check_news_moderation_every_10_min': {
        'task': 'news.tasks.check_moderation_status',
        'schedule': 600.0,
    },
    'ingredients_popularity_reset_every_day': {
        'task': 'recipes.tasks.ingredients_popularity_reset',
        'schedule': crontab(hour=0, minute=0),
    },
}

# email
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_PORT = env('EMAIL_PORT')
EMAIL_USE_SSL = env('EMAIL_USE_SSL')

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# static

STATIC_URL = '/static/'

if DEBUG:
    STATICFILES_DIRS = [
        BASE_DIR / 'static'
    ]
else:
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# media

MEDIA_ROOT = BASE_DIR / 'media/'
MEDIA_URL = 'media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# User
AUTH_USER_MODEL = "users.User"