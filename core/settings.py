# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from decouple import config
from envparse import env
from django.urls import reverse_lazy
from unipath import Path
from django.contrib.messages import constants as messages
import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = Path(__file__).parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_1122')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=False, cast=bool)

# load production server from .env
ALLOWED_HOSTS = ['*', 'localhost', '127.0.0.1', config('SERVER', default='127.0.0.1')]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'logger',
    'mail',
    'fontawesomefree',
    'app',
    'generic',
    'triage',
    'dashboards',
    'crispy_forms',
    'rest_framework'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'logger.middlewares.CurrentUserMiddleware',
    'logger.middlewares.ErrorMiddleware',
]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "home"   # Route defined in app/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in app/urls.py

TEMPLATE_DIR = os.path.join(CORE_DIR, "core/templates")  # ROOT dir for templates
TEMPLATE_DIR_TRIAGE = os.path.join(CORE_DIR, "triage/templates")  # ROOT dir for templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR, TEMPLATE_DIR_TRIAGE],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.cms_context',
            ],
        },
    },
]

BASE_TEMPLATE = "layouts/base.html"

WSGI_APPLICATION = 'core.wsgi.application'

# Rest Framework
REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
     )
 }

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME'  : os.path.join(CORE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'it'

TIME_ZONE = 'Europe/Rome'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# import locale
# locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')

#############################################################
# SRC: https://devcenter.heroku.com/articles/django-assets

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_ROOT = os.path.join(CORE_DIR, 'staticfiles')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(CORE_DIR, 'media').replace('\\', '/')
MEDIA_URL = '/media/'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(CORE_DIR, 'core/static'),
)
#############################################################
#############################################################

DEBUG_PERFORMANCE= env("DEBUG_PERFORMANCE",cast=bool, default=False)
if DEBUG_PERFORMANCE:
    INSTALLED_APPS += ['debug_toolbar', 'silk']
    INTERNAL_IPS = ['127.0.0.1']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    MIDDLEWARE.append('silk.middleware.SilkyMiddleware')

    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
    ]

#DFX
LICENCE_KEY=env("LICENCE_KEY", default='73b74e60-1bdb-465b-9d62-28667ac6caca')
ORG_KEY=env("ORG_KEY", default='padmed')
DFX_USER=env("DFX_USER", default='alessandro.pellegrino@padmed.com')
DFX_PASSWORD=env("DFX_PASSWORD", default='P4dm35!')

#DEEP AFFEX MEASUREMENT SETTINGS
CHUNK_DURATION=env("CHUNK_DURATION", cast=float, default=5)
DEEPAFFEX_DEBUG=env("DEEPAFFEX_DEBUG", cast=bool, default=False)
DEEPAFFEX_DEBUG_SAVE_CHUNKS_FOLDER=env("DEEPAFFEX_DEBUG_SAVE_CHUNKS_FOLDER", cast=str, default=os.path.join(MEDIA_ROOT, "debug_chunks"))
## CUSTOM SETTINGS VARIABLES FOR GRAPHS
INIT_MAX_WAITING_SECONDS = env("INIT_MAX_WAITING_SECONDS", cast=float, default=2400)

## CRISPY FORM SETTINGS 
CRISPY_TEMPLATE_PACK = 'bootstrap4'

## MESSAGES 
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
MESSAGE_TAGS = {
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'danger',
}

## DEFAULTS PRIMARY KEYS 
DEFAULT_AUTO_FIELD='django.db.models.AutoField' 

## Behaviour variables
USE_CARD_READER = env("USE_CARD_READER", cast=bool, default=True)
ROTATE_90_COUNTERCLOCKWISE = env("ROTATE_90_COUNTERCLOCKWISE", cast=bool, default=True)