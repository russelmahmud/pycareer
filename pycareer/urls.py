from django.conf.urls import url, patterns, include
from django.conf.urls.static import static
from django.conf import settings
from django.http import HttpResponsePermanentRedirect

# django admin
from django.contrib import admin
admin.autodiscover()

# search for dbindexes.py in all INSTALLED_APPS and load them
import dbindexer
dbindexer.autodiscover()

handler500 = 'djangotoolbox.errorviews.server_error'


def redirect_permanent(base_url):
    def redirect(request, path):
        return HttpResponsePermanentRedirect(base_url + path)
    return redirect


urlpatterns = patterns(
    '',
    url(r'^_ah/warmup$', 'djangoappengine.views.warmup'),
    url(r'^admin37/', include(admin.site.urls)),
    url(r'^account/', include('pycareer.account.urls')),
    url(r'^jobs/', include('pycareer.job.urls')),
    url(r'^events/', include('pycareer.event.urls')),
    url(r'^books/', include('pycareer.book.urls')),
    url(r'^python-jobs/(?P<path>.*)$', redirect_permanent('/jobs/')),
    url(r'^python-events/(?P<path>.*)$', redirect_permanent('/events/')),
    url(r'^tasks/aggregate_job/', 'pycareer.tasks.start_aggregation'),
    url(r'^tasks/archive_job/', 'pycareer.tasks.archive_old_job'),
    url(r'^tasks/extract_events/', 'pycareer.tasks.extract_events'),
    url('^', include('pycareer.core.urls')),
)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
