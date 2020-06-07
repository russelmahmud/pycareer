from django.conf.urls import patterns, url
from django.contrib.sitemaps.views import sitemap
from django.views.generic.simple import direct_to_template, redirect_to
from django.conf import settings

from .views import ContactView, NewsletterView
from .sitemap import sitemap_dict


urlpatterns = patterns(
    '',
    url('^$', 'pycareer.core.views.homepage', name='home_page'),
    url(r'^load_data/$', 'pycareer.core.views.load_initial_data'),
    url(r'^reindex_all_jobs/$', 'pycareer.core.views.reindex_jobs'),
    url('^contact/$', ContactView.as_view(), name='contact_page'),
    url(r'^newsletter/$', NewsletterView.as_view(), name='newsletter_page'),
    url('^privacy/$', 'pycareer.core.views.privacy', name='privacy_page'),
    url(r'^robots\.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    url(r'^ads\.txt$', direct_to_template, {'template': 'ads.txt', 'mimetype': 'text/plain'}),
    url(r'^favicon\.ico$', redirect_to, {'url': settings.STATIC_URL + 'img/favicon.ico'}),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemap_dict}, name='sitemaps')
)
