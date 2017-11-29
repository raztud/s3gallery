from django.conf.urls import url
from browser.views import IndexView, ShowFileView, ShowFileRedirectView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^show-file/$', ShowFileRedirectView.as_view(), name='show-file'),
    url(r'^file/(?P<element>[a-zA-Z_0-9\-\/\.,\(\)]+)$', ShowFileView.as_view(), name='file'),
]
