import logging
import base64
import time
from django.views import View
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
from browser.s3browser import S3Browser, S3BrowserExceptionNotFound, \
    S3BrowserReadingError

logger = logging.getLogger('gallery')


class ShowFileView(View):
    def get(self, request, element=None):
        if element is None:
            element = request.GET.get('element')

        if element is None:
            return HttpResponseNotFound()

        filename = '{}{}'.format(settings.ROOT_FULL, element)
        s3browser = S3Browser()
        try:
            body, content_type = s3browser.get_raw_file(filename, cache=True)
            return render(request, 'show-file.html', {
                'imgbody': base64.b64encode(body),
                'year': time.strftime("%Y"),
            })
        except S3BrowserExceptionNotFound:
            return HttpResponseNotFound()
        except S3BrowserReadingError:
            return HttpResponse('Please try again later.')
