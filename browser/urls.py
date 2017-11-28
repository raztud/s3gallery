from django.conf.urls import url
from browser.views import IndexView, ShowFileView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^show-file/$', ShowFileView.as_view(), name='show-file'),
    url(r'^file/(?P<element>[a-zA-Z_0-9\-\/\.,]+)$', ShowFileView.as_view(), name='file'),
]
