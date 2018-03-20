# coding: utf-8

from django.conf.urls import url
from browser.views import IndexView, ShowFileView, \
    ShowFileRedirectView, IndexViewRedirect, UploadView, SetThumbs
from django.contrib.auth.decorators import permission_required

urlpatterns = [
    url(r'^$', IndexViewRedirect.as_view(), name='home'),
    url(r'^folder/(?P<element>.*?)$', IndexView.as_view(), name='index'),
    url(r'^show-file/$', ShowFileRedirectView.as_view(), name='show-file'),
    url(r'^file/(?P<element>.+)$', ShowFileView.as_view(), {'raw': False}, name='file'),
    url(r'^raw-file/(?P<element>.+)$', ShowFileView.as_view(), {'raw': True}, name='raw-file'),
    url(r'^upload/$', UploadView.as_view(), name='upload'),
    url(r'^set-thumb/$', permission_required('is_staff', '/admin')(SetThumbs.as_view()), name='set-thumb'),
]
