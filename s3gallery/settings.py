"""
Django settings for s3gallery project.

Generated by 'django-admin startproject' using Django 1.10.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os
from django.utils.translation import ugettext_lazy as _

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ugettext = lambda s: s

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7s9ki=1hun37691kwn+47l9=rn+5ibt2bly+3ywrdujk@p^7c)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['s3gallery.ursultrubadur.org', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'browser'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 's3gallery.urls'

TEMPLATE_DEBUG = DEBUG # django is stupid...dont put it in TEMPLATES

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
                'browser.context_processors.site_configs',
                'django.template.context_processors.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 's3gallery.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 's3gallery',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

SILENCED_SYSTEM_CHECKS = ['mysql.E001']

# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'ro'

LANGUAGES = (
    ('ro', _('Română')),
    ('en', _('English')),
)

# LOCALE_PATHS = (
#     os.path.join(BASE_DIR, 'locale'),
# )

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = '/static/'

DJANGO_LOG_LEVEL = DEBUG
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '{}/logs/s3browser.log'.format(BASE_DIR),
            'formatter': 'simple',
        },
    },
    'loggers': {
        'gallery': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

TMP_FOLDER = '{}/temporary'.format(BASE_DIR)

MEDIA_URL = TMP_FOLDER + '/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads')
STATIC_ROOT = os.path.join(BASE_DIR, 'public_html')

RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''

SITE_ADMIN = 'no-mail@mail.com'

EMAIL_USE_TLS = True
EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 1025

# exposed settings
# all the following settings can be used in templates with lower case
SITE_NAME = 'Photo gallery'
SITE_DESCRIPTION = 'This is my photo gallery'
META_TITLE = 'My photos'
META_DESCRIPTION = 'Simple S3 Browser for photos'
META_KEYWORDS = 'gallery, photo'
COPYRIGHT = 's3browser'
HOME_WEBSITE = 'http://mydomain.com/'
FACEBOOK_URL = 'https://www.facebook.com/myuser/'
# end exposed settings

from .amazon import ACCESS_KEY, SECRET_KEY, REGION, BUCKET, ROOT, ROOT_FULL, AWS_URL

try:
    from .settings_dev import *
except ImportError as e:
    pass

try:
    from .settings_prod import *
except ImportError as e:
    pass
