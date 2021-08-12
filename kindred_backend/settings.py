"""
Django settings for kindred_backend project.

Generated by 'django-admin startproject' using Django 3.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

from datetime import timedelta
from pathlib import Path
import environ
import os
import redis
import django_rq


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env_file = os.path.join(BASE_DIR, '.env')

env = environ.Env()

environ.Env.read_env(env_file)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True if int(env('DEBUG')) == 1 else False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'kindred',
    'django_rq',
    'rest_framework',
    'corsheaders',
    'phonenumber_field',
    'location_field.apps.DefaultConfig'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

ROOT_URLCONF = 'kindred_backend.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'kindred_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('POSTGRES_DB'),
        'USER': env('POSTGRES_USER'),
        'PASSWORD': env('POSTGRES_PASSWORD'),
        'HOST': 'db',
        'PORT': env('POSTGRES_PORT'),
    }
}

RQ_QUEUES = {
    'default': {
        'HOST': 'redis',
        'PORT': env('REDIS_PORT'),
        'DB': 0,
        'PASSWORD': env('REDIS_PASSWORD'),
        'DEFAULT_TIMEOUT': 360,
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Redis queue

redis_cursor = redis.Redis(host='redis', port=env('REDIS_PORT'), db=0, username='default', password=env('REDIS_PASSWORD'))
cache_db = redis.Redis(
    host='redis', port=env('REDIS_PORT'), db=1, username='default', password=env('REDIS_PASSWORD'),
    charset="utf-8", decode_responses=True
)
queue = django_rq.get_queue('default', connection=redis_cursor , autocommit=True, is_async=True, default_timeout=360)

# CORS

CORS_ALLOW_ALL_ORIGINS = True

AUTH_USER_MODEL = 'users.User'

PHONENUMBER_DB_FORMAT = 'INTERNATIONAL'

DEFAULT_AUTO_FIELD='django.db.models.AutoField'

LOCATION_FIELD = {
    'map.provider': 'openstreetmap',
    'search.provider': 'nominatim',
}

WEBSOCKET_URL = env('WEBSOCKET_URL')

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=env(var='ACCESS_TOKEN_LIFETIME', cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env(var='REFRESH_TOKEN_LIFETIME', cast=int)),
}

DATA_UPLOAD_MAX_MEMORY_SIZE = 50000000

