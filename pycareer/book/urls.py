from django.conf.urls import patterns, url

from .views import book_list, book_details

urlpatterns = patterns(
    '',
    url(r'^(?P<id_>\d+)/(?P<slug>[\w-]+)/$', book_details, name='book_details'),
    url(r'^$', book_list, name='book_list'),
)
