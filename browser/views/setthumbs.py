# coding: utf-8
import logging
from urllib.parse import unquote
from django.shortcuts import render
from django.urls import resolve
from django.http import HttpResponseBadRequest, JsonResponse
from django.views import View
from browser.models.folders import Folders

logger = logging.getLogger('gallery')


class SetThumbs(View):
    template_name = 'set-thumb.html'

    def get(self, request):
        thumb = request.GET.get('thumb', '')
        path = request.GET.get('path', '')
        if not path or not thumb:
            return HttpResponseBadRequest('Invalid path or thumb')

        match = resolve(path)
        path = match.kwargs.get('element')
        if not path:
            return HttpResponseBadRequest('Invalid path')

        elements = [x for x in path.split('/') if x]

        paths = []
        for x in range(len(elements)):
            el = '/'.join(elements[:x + 1]) + '/'
            paths.append(el)

        return render(request, self.template_name, {
            'paths': paths,
            'thumb': thumb,
            'original_path': path,
        })

    def post(self, request):
        thumb = request.POST.get('thumb')
        folder_path = request.POST.get('folderPath')
        originalPath = request.POST.get('original_path')
        if not thumb or not folder_path:
            return HttpResponseBadRequest('Invalid path or thumb')

        # todo: validate
        preview_thumb = unquote(originalPath + thumb.replace('thumb_', ''))
        logging.error('preview Thumb 2: {}'.format(preview_thumb))
        folder = Folders()
        folder.s3url = unquote(folder_path)
        folder.preview_thumb = preview_thumb
        folder.save()

        return JsonResponse(
            {'ok': True, 'thumb':  thumb, 'folderPath': folder_path}
        )
