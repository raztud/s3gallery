# coding: utf-8
import logging
import base64
import time
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound, \
    HttpResponsePermanentRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from browser.s3browser import S3Browser, S3BrowserExceptionNotFound, \
    S3BrowserReadingError

logger = logging.getLogger('gallery')


class ShowFileView(View):
    def get(self, request, raw=False, element=None):
        if element is None:
            element = request.GET.get('element')

        if element is None:
            return HttpResponseNotFound()

        filename = '{}{}'.format(settings.ROOT_FULL, element)
        s3browser = S3Browser()
        try:
            body, content_type = s3browser.get_raw_file(filename, cache=True)
            if raw:
                return HttpResponse(
                    body, content_type=content_type
                )

            return render(request, 'show-file.html', {
                'imgbody': base64.b64encode(body).decode('utf-8'),
                'year': time.strftime("%Y"),
                'filename': element
            })
        except S3BrowserExceptionNotFound:
            return HttpResponseNotFound()
        except S3BrowserReadingError:
            return HttpResponse('Please try again later.')


class ShowFileRedirectView(View):

    def get(self, request):
        element = request.GET.get('element', '')
        return HttpResponsePermanentRedirect(reverse('file', args=(element,)))

