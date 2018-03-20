# coding: utf-8
import logging
import time

from django.views import View
from django.shortcuts import render, reverse
from django.conf import settings
from django.http import HttpResponsePermanentRedirect

from browser.models import Thumb, Folders
from browser.s3browser import S3Browser

logger = logging.getLogger('gallery')


def update_folder_list(folders):
    for entry in folders:
        entry['preview_thumb'] = ''

        try:
            meta_info = Folders.objects.get(s3url=entry['full_path'])
            preview_image = meta_info.preview_thumb
        except Folders.DoesNotExist:
            preview_image = None

        if not preview_image:
            continue

        try:
            thumb = Thumb.objects.get(s3url=preview_image)
            entry['preview_thumb'] = '{}{}'.format(settings.AWS_URL,
                                                   thumb.thumb_path)
        except Thumb.DoesNotExist:
            pass


class IndexViewRedirect(View):
    """
    TODO: Merge with IndexView
    """
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
        description = name = ''
        try:
            meta_info = Folders.objects.get(s3url=element)
            description = meta_info.description
            name = meta_info.name
        except Folders.DoesNotExist:
            pass

        update_folder_list(file_list['folders'])

        elements = {
            'meta_description': description,
            'meta_folder_name': name,
            'real_folder_name': 'Home',
            'real_path': '/',
            'elements': [current_element],
            'current_element': current_element,
            'folders': file_list['folders'],
            'files': file_list['files'],
            'year': time.strftime("%Y"),
        }

        # logging.debug("elements1 = {}".format(elements))

        return render(request, self.template_name, {'data': elements})


class IndexView(View):
    template_name = 'index.html'

    def get(self, request, element=''):
        prefix = settings.ROOT_FULL + element

        s3browser = S3Browser()
        file_list = s3browser.get_list(prefix=prefix)

        current_element = element or 'Photo Gallery '
        current_element = current_element.replace('_', ' ')[:-1]

        breadcrumbs = []
        path = ''
        for el in element.split('/'):
            if not el:
                continue
            path += el + '/'
            link = reverse('index', args=[path])
            breadcrumbs.append((el, link))

        for filedata in file_list['files']:
            filename_path = filedata['full_path']
            try:
                t = Thumb.objects.get(s3url=filename_path)
                thumb_path = t.thumb_path
            except Thumb.DoesNotExist:
                aws_filepath = '{}{}'.format(settings.ROOT,
                                             filedata['full_path'])
                etag = s3browser.has_thumb(aws_filepath)
                thumb_path = ''
                if etag:
                    thumb_name = 'thumb_' + filename_path.split('/')[-1]
                    thumb_path = '/'.join(
                        filename_path.split('/')[:-1]) + '/' + thumb_name

                    t = Thumb()
                    t.s3url = filename_path
                    t.md5sum = etag
                    t.thumb_path = thumb_path
                    t.save()

            filedata['thumb'] = '{}{}'.format(settings.AWS_URL,
                                              thumb_path)

        description = name = ''
        try:
            meta_info = Folders.objects.get(s3url=element)
            description = meta_info.description
            name = meta_info.name
        except Folders.DoesNotExist:
            pass

        update_folder_list(file_list['folders'])

        elements = {
            'meta_description': description,
            'meta_folder_name': name,
            'real_folder_name': breadcrumbs[-1][0],
            'real_path': breadcrumbs[-1][1],
            'breadcrumbs': breadcrumbs,
            'current_element': current_element,
            'folders': file_list['folders'],
            'files':  file_list['files'],
            'year': time.strftime('%Y'),
        }

        return render(request, self.template_name, {'data': elements})

