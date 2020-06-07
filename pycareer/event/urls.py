from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from .views import EventsFeed, EventFormView, event_list, event_details, event_archives, event_list_api

urlpatterns = patterns(
    '',
    url(r'^feed/rss/$', EventsFeed(), name='event_rss'),
    url(r'^submit/$', login_required(EventFormView.as_view()), name='event_submit'),
    url(r'^(?P<id_>\d+)/(?P<slug>[\w-]+)/$', event_details, name='event_details'),
    url(r'^past/$', event_archives, name='event_archives'),
    url(r'^api/$', event_list_api),
    url(r'^$', event_list, name='event_list'),
)
