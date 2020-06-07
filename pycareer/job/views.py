from django.shortcuts import render_to_response, Http404, HttpResponseRedirect
from django.template import RequestContext
from django.conf import settings
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse_lazy, reverse
from django.views.generic import FormView, DetailView, UpdateView, ListView
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from pycareer import log
from pycareer.core.paginator import Paginator
from pycareer.core.countries import SORTED_COUNTRIES, get_country_by_slug
from pycareer.services import get_service, NotFoundError, SearchError, ValidationError
from pycareer.services.schema.job import SearchRequestSchema
from pycareer.services.utils import validate
from .forms import JobForm
from .models import APPROVED

logger = log.get_logger()
job_service = get_service('job')
job_search_service = get_service('job_search')
indeed_service = get_service('indeed')
email_service = get_service('email')


class JobCreateView(FormView):
    form_class = JobForm
    http_method_names = ['get', 'post']
    template_name = 'job/create.html'

    def get_context_data(self, **kwargs):
        kwargs['jobs'] = job_service.active_jobs(limit=5)['items']
        kwargs['countries'] = SORTED_COUNTRIES
        return kwargs

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        profile = self.request.user.get_profile()
        self.initial['contact_email'] = profile.user.email
        self.initial['contact_name'] = profile.user.get_full_name()
        self.initial['company_name'] = profile.company_name
        self.initial['company_description'] = profile.company_description
        return self.initial.copy()

    def form_valid(self, form):
        form.cleaned_data['submitted_by'] = self.request.user.id

        try:
            job = job_service.create(form.cleaned_data)
            self.request.session['job_url'] = job['url']
        except ValidationError:
            logger.exception('Validation error in service layer.')
            raise

        try:
            email_service.send_support(subject='New job has submitted for review',
                                       template='emails/new_job_template.html',
                                       ctx=job)
        except Exception:
            logger.exception('Exception while sending email after job creation.')

        return super(JobCreateView, self).form_valid(form)

    def get_success_url(self):
        return self.request.session['job_url']


class JobUpdateView(UpdateView):
    form_class = JobForm
    http_method_names = ['get', 'post']
    template_name = 'job/update.html'

    def get_context_data(self, **kwargs):
        kwargs['jobs'] = job_service.active_jobs(limit=5)['items']
        kwargs['countries'] = SORTED_COUNTRIES
        return kwargs

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instanciating the form.
        """
        kwargs = super(JobUpdateView, self).get_form_kwargs()
        kwargs.pop('instance')
        kwargs.update({'initial': self.object})
        return kwargs

    def get_object(self, queryset=None):
        id_ = self.kwargs.get('id_')
        try:
            job = job_service.get(id_)
        except NotFoundError:
            raise Http404

        if not job_service.is_owner(job, self.request.user):
            messages.warning(self.request, 'You do not own this job post. You can update your listings only.',
                             extra_tags='permission')
            raise PermissionDenied

        return job

    def form_valid(self, form):
        try:
            job_service.update(self.kwargs.get('id_'), form.cleaned_data)
        except ValidationError:
            logger.exception('Validation error in service layer.')
            raise

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return self.object['url']


class JobDetailsView(DetailView):
    template_name = 'job/details.html'
    context_object_name = 'job'
    http_method_names = ['get']

    def get_object(self, queryset=None):
        id_ = self.kwargs.get('id_')
        try:
            job = job_service.get(id_)
            job['full_url'] = self._build_full_url(job['url'])
            job['is_owner'] = job_service.is_owner(job, self.request.user)
        except NotFoundError:
            raise Http404

        return job

    def get_context_data(self, **kwargs):
        kwargs = super(JobDetailsView, self).get_context_data(**kwargs)
        kwargs['countries'] = SORTED_COUNTRIES
        return kwargs

    def _build_full_url(self, path):
        return self.request.build_absolute_uri(path)


class MyJobs(ListView):
    template_name = 'account/jobs.html'
    context_object_name = 'jobs'

    def get_context_data(self, **kwargs):
        kwargs['APPROVED'] = APPROVED
        return super(MyJobs, self).get_context_data(**kwargs)

    def get_queryset(self):
        return job_service.my_jobs(self.request.user.id)['items']


def job_list_co(request, code):
    query = request.GET.get('q')
    if not query:
        query = 'python'

    country = get_country_by_slug(code)

    if not country:
        raise Http404

    page = Paginator.validate_number(request.GET.get('page'))
    offset = settings.LIST_PAGE_SIZE * (page - 1)
    search_request = validate(SearchRequestSchema(), {
        'query': query,
        'offset': offset,
        'sort': request.GET.get('sort')
    })
    api_response = job_search_service.search(search_request, code=country['code'])
    total_items = len(api_response['items'])
    limit = search_request['limit'] - total_items

    if limit:
        start = offset + total_items - api_response['num_found']
        indeed_query = 'title:python ' + query
        resp = indeed_service.search(indeed_query, start=start, limit=limit, co=country['code'])
        api_response['items'].extend(resp['items'])
        api_response['num_found'] += resp['num_found']

    return render_to_response('job/list_loc.html', {
        'query': query,
        'jobs': api_response['items'],
        'country': country,
        'countries': SORTED_COUNTRIES,
        'paginator': Paginator(page, api_response['num_found'])
    }, context_instance=RequestContext(request))


def job_list(request):
    query = request.GET.get('q', '')
    page = Paginator.validate_number(request.GET.get('page'))
    offset = settings.LIST_PAGE_SIZE * (page - 1)

    search_request = validate(SearchRequestSchema(), {
        'query': query.encode('utf-8').replace(',', ' ').strip(),
        'offset': offset,
        'sort': request.GET.get('sort')
    })

    try:
        resp = job_search_service.search(search_request)
    except SearchError:
        logger.exception('Search failed for request %s' % search_request)
        raise

    return render_to_response('job/list.html', {
        'query': query,
        'countries': SORTED_COUNTRIES,
        'jobs': resp['items'],
        'paginator': Paginator(page, resp['num_found'])
    }, context_instance=RequestContext(request))


def delete(request, id_):
    try:
        job = job_service.get(id_)
    except NotFoundError:
        raise Http404

    if not job_service.is_owner(job, request.user):
        messages.warning(request, 'You do not own this job post. You can delete only your listings.',
                         extra_tags='permission')
        raise PermissionDenied

    if job['status'] == APPROVED:
        messages.warning(request, 'You can not delete the approved listing. Try to archive it.',
                         extra_tags='permission')
        return HttpResponseRedirect(reverse('jobs_mine'))

    job_service.delete(id_)

    return HttpResponseRedirect(reverse('jobs_mine'))


def archive(request, id_):
    try:
        job = job_service.get(id_)
    except NotFoundError:
        raise Http404

    if not job_service.is_owner(job, request.user):
        messages.warning(request, 'You do not own this job post. You can archive only your listings.',
                         extra_tags='permission')
        raise PermissionDenied

    if job['status'] != APPROVED:
        messages.warning(request, 'You can only archive the approved listing. Try to delete it.',
                         extra_tags='permission')
        return HttpResponseRedirect(reverse('jobs_mine'))

    job_service.archive(id_)

    return HttpResponseRedirect(reverse('jobs_mine'))


def get_contact_info(request, id_):
    job = job_service.get(id_)
    return render_to_response('job/contact_info.html', {
        'job': job
    }, context_instance=RequestContext(request))


class JobsFeed(Feed):
    title = "Python Jobs"
    link = reverse_lazy('job_rss')
    description = "Latest python jobs in PyCareer"

    def items(self):
        return job_service.latest_jobs(limit=settings.RSS_PAGE_SIZE)

    def item_title(self, item):
        return "%s - %s" % (item['title'], item['location'])

    def item_description(self, item):
        return item['description']

    def item_link(self, item):
        return item['url']

    def item_pubdate(self, item):
        return item['created_at']

    def item_guid(self, item):
        return str(item['id'])
