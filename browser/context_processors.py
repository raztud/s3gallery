from django.conf import settings


def site_configs(request):
    return {
        'site_name': settings.SITE_NAME,
        'copyright': settings.COPYRIGHT,
    }
