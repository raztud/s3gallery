from django.views import View
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
from browser.s3browser import S3Browser, S3BrowserExceptionNotFound, S3BrowserReadingError


class ShowFileView(View):
    def get(self, request):
        if not request.GET.get('element', None):
            return HttpResponseNotFound()

        filename = settings.ROOT_FULL + request.GET.get('element')
        s3browser = S3Browser()
        try:
            body, content_type = s3browser.get_raw_file(filename, cache=True)
        except S3BrowserExceptionNotFound:
            return HttpResponseNotFound()
        except S3BrowserReadingError:
            return HttpResponse('Please try again later.')

        return HttpResponse(body, content_type=content_type)
