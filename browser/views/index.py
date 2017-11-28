import logging

from django.views import View
from django.shortcuts import render
from django.conf import settings

from browser.s3browser import S3Browser

logger = logging.getLogger('gallery')


class IndexView(View):
    template_name = 'index.html'

    def get(self, request):
        prefix = settings.ROOT_FULL + request.GET.get('element', '')

        s3browser = S3Browser()
        file_list = s3browser.get_list(prefix=prefix)

        current_element = request.GET.get(
            'element',
            'Photo Gallery ').replace('_', ' ')[:-1]

        elements = current_element.split('/')

        elements = {
            'elements': elements,
            'current_element': current_element,
            'folders': file_list['folders'],
            'files':  file_list['files']
        }

        return render(request, self.template_name, {'data': elements})
