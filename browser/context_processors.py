# coding: utf-8

from django.conf import settings


def site_configs(request):
    return {
        'site_name': settings.SITE_NAME,
        'site_description': settings.SITE_DESCRIPTION,
        'meta_title': settings.META_TITLE,
        'meta_description': settings.META_DESCRIPTION,
        'meta_keywords': settings.META_KEYWORDS,
        'home_website': settings.HOME_WEBSITE,
        'facebook_url': settings.FACEBOOK_URL,
        'copyright': settings.COPYRIGHT,
    }
