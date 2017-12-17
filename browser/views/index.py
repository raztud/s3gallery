import logging

from django.views import View
from django.shortcuts import render, reverse
from django.conf import settings
from django.http import HttpResponsePermanentRedirect

from browser.s3browser import S3Browser

logger = logging.getLogger('gallery')


class IndexViewRedirect(View):
    template_name = 'index.html'

    def get(self, request):

        element = request.GET.get('element', '')
        if element != '':
            return HttpResponsePermanentRedirect(
                reverse('index', args=(request.GET.get('element', ''),))
            )

        s3browser = S3Browser()
        file_list = s3browser.get_list(prefix=settings.ROOT_FULL)

        current_element = 'Photo Gallery '

        elements = {
            'elements': [current_element],
            'current_element': current_element,
            'folders': file_list['folders'],
            'files': file_list['files']
        }

        return render(request, self.template_name, {'data': elements})


class IndexView(View):
    template_name = 'index.html'

    def get(self, request, element=''):
        prefix = settings.ROOT_FULL + element

        s3browser = S3Browser()
        file_list = s3browser.get_list(prefix=prefix)

        current_element = element or 'Photo Gallery '
        current_element = current_element.replace('_', ' ')[:-1]

        elements = current_element.split('/')

        thumbs = {}
        for filedata in file_list['files']:
            # print(filedata)
            filename_path = filedata['full_path']
            tokens = filename_path.split('/')
            filename = tokens[-1]
            path = '/'.join(tokens[:-1])
            thumb_name = '{}/thumb_{}'.format(path, filename)
            filedata['thumb'] = settings.AWS_URL + thumb_name
            # thumbs[filename] = 'https://s3-eu-west-1.amazonaws.com/utgal/g3/21645e22db975037a385a03701f2683c/fs/MuntiiLor/2006_mont_blanc/ep1_coumayeur/thumb_IMG_2466.JPG'

        print(file_list['files'])

        elements = {
            'elements': elements,
            'current_element': current_element,
            'folders': file_list['folders'],
            'files':  file_list['files']
        }

        return render(request, self.template_name, {'data': elements})
