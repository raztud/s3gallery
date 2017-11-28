from django.conf.urls import url
from browser.views import IndexView, ShowFileView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^show-file/$', ShowFileView.as_view(), name='show-file'),
]
