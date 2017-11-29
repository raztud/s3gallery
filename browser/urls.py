from django.conf.urls import url
from browser.views import IndexView, ShowFileView, ShowFileRedirectView, IndexViewRedirect

urlpatterns = [
    url(r'^$', IndexViewRedirect.as_view(), name='index1'),
    url(r'^folder/(?P<element>.+)$', IndexView.as_view(), name='index'),
    url(r'^show-file/$', ShowFileRedirectView.as_view(), name='show-file'),
    url(r'^file/(?P<element>.+)$', ShowFileView.as_view(), name='file'),
]
