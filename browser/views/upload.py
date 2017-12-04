import time
import logging
import random
from django.shortcuts import render
from django.views import View
from browser.forms import UploadFileForm
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail


logger = logging.getLogger('gallery')


class UploadView(View):
    template_name = 'upload.html'

    def get(self, request):
        return render(request, 'upload.html', {'form': UploadFileForm()})

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, 'upload.html', {
                'form': UploadFileForm(),
                'message': 'Invalid request',
                'error': True,
            })

        myfile = request.FILES['uploadedfile']
        filename = self._get_filename(myfile.name)

        fs = FileSystemStorage()
        fs.save(filename, myfile)
        comment = request.POST.get('comment', '')

        try:
            send_mail(
                '[UT] Fisier nou uploadat',
                'Fisier: {}; Comentariu: {}'.format(filename, comment),
                'root@s3gallery.razvantudorica.net',
                ['razvantudorica@gmail.com'],
                fail_silently=False,
            )
        except:
            logger.error('Could not send email: {} {}'.format(filename, comment))

        return render(request, 'upload.html', {
            'form': UploadFileForm(),
            'message': 'Success',
            'error': False,
        })

    @staticmethod
    def _get_extension(filename):
        ext = filename.split('.')[-1]
        if ext == filename:
            return ''

        return ext

    @staticmethod
    def _get_filename(fname):
        letter = chr(random.randrange(97, 97 + 26 + 1))
        ext = UploadView._get_extension(fname)
        return '{}_{}.{}'.format(letter, int(time.time()), ext)
