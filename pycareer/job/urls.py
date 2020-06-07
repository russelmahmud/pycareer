from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from pycareer.account.decorators import recruiter_only
from .views import (
    job_list,
    job_list_co,
    delete,
    archive,
    get_contact_info,
    JobDetailsView,
    JobsFeed,
    JobCreateView,
    JobUpdateView,
    MyJobs,
)

urlpatterns = patterns(
    '',
    url(r'^feed/rss/$', JobsFeed(), name='job_rss'),
    url(r'^mine/$', recruiter_only(MyJobs.as_view()), name='jobs_mine'),
    url(r'^post/$', recruiter_only(JobCreateView.as_view()), name='job_post'),
    url(r'^(?P<id_>\d+)/edit/$', login_required(JobUpdateView.as_view()), name='job_update'),
    url(r'^(?P<id_>\d+)/delete/$', login_required(delete), name='job_delete'),
    url(r'^(?P<id_>\d+)/archive/$', login_required(archive), name='job_archive'),
    url(r'^(?P<id_>\d+)/contact-info/$', get_contact_info, name='job_contact_info'),
    url(r'^in/(?P<code>[\w]+)/$', job_list_co, name='job_list_co'),
    url(r'^(?P<id_>\d+)/(?P<slug>[\w-]+)/$', JobDetailsView.as_view(), name='job_details'),
    url(r'^$', job_list, name='job_list'),
)
