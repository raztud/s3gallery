import logging
from django.shortcuts import render
from django.views import View
from browser.forms import UploadFileForm

logger = logging.getLogger('gallery')


class UploadView(View):
    template_name = 'upload.html'

    def get(self, request):
        return render(request, 'upload.html', {'form': UploadFileForm()})

    def post(self, request):
        form = UploadFileForm(request.POST, request.FILES)
        # if form.is_valid():
        #     handle_uploaded_file(request.FILES['file'])
        #     return HttpResponseRedirect('/success/url/')
