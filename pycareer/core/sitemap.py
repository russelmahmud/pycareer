from django.contrib import sitemaps
from django.core.urlresolvers import reverse

from .countries import SORTED_COUNTRIES


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['home_page', 'contact_page', 'registration_register', 'auth_login']

    def location(self, item):
        return reverse(item)


class ListSitemap(sitemaps.Sitemap):
    priority = 0.9
    changefreq = 'hourly'

    def items(self):
        return ['job_list', 'event_list']

    def location(self, item):
        return reverse(item)


class JobsSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return SORTED_COUNTRIES

    def location(self, item):
        return reverse('job_list_co', args=(item['slug'], ))


sitemap_dict = {
    'static': StaticViewSitemap,
    'list': ListSitemap,
    'jobs': JobsSitemap
}
