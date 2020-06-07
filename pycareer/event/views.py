import json

from django.views.generic.edit import FormView
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages
from django.contrib.syndication.views import Feed

from pycareer import log
from pycareer.services.utils import DateTimeEncoder
from pycareer.services import get_service, NotFoundError, ValidationError
from .forms import EventForm

logger = log.get_logger()
event_service = get_service('event')
email_service = get_service('email')


class EventFormView(FormView):
    form_class = EventForm
    http_method_names = ['get', 'post']
    template_name = 'event/submit.html'

    def get_context_data(self, **kwargs):
        kwargs['events'] = event_service.active_events()[:5]
        return kwargs

    def form_valid(self, form):
        form.cleaned_data['submitted_by'] = self.request.user.id
        try:
            event_service.create(form.cleaned_data)
        except ValidationError:
            logger.exception('Validation error in service layer.')
            raise

        try:
            email_service.send_support(subject='New Event Submitted for Review',
                                       template='emails/new_event_template.html',
                                       ctx=form.cleaned_data)
        except Exception:
            logger.exception('Exception while sending email after event creation.')

        messages.success(self.request, 'Thank you! Your event has been successfully submitted for review.',
                         extra_tags='event')
        return super(EventFormView, self).form_valid(form)

    def get_success_url(self):
        return reverse('event_submit')


def event_list(request):
    pycon_events = event_service.upcoming_events(limit=10, event_type='Python Events')
    user_events = event_service.upcoming_events(limit=10, event_type='User Group Events')
    past_events = event_service.past_events()
    return render_to_response('event/map.html', {
        'title': 'Python Events',
        'pycon_events': pycon_events,
        'user_events': user_events,
        'past_events': past_events[:10]
    }, context_instance=RequestContext(request))


def event_list_api(request):
    id_ = request.GET.get('id')
    if id_:
        events = [event_service.get(id_)]
    else:
        events = event_service.active_events()
    events = list(filter(lambda x: x['lat'] and x['lon'], events))
    jsondata = json.dumps(events, cls=DateTimeEncoder)
    return HttpResponse(jsondata, content_type='application/json')


def event_archives(request):
    events = event_service.past_events()
    return render_to_response('event/list.html', {
        'events': events,
        'title': 'Past Python Events'
    }, context_instance=RequestContext(request))


def event_details(request, id_, slug):
    try:
        event = event_service.get(id_)
        event['full_url'] = request.build_absolute_uri(event['url'])
    except NotFoundError:
        raise Http404

    return render_to_response('event/details.html', {
        'event': event,
        'is_archived': event_service.is_archived(event['id'])
    }, context_instance=RequestContext(request))


class EventsFeed(Feed):
    title = 'Python Events'
    link = reverse_lazy('event_rss')
    description = 'Latest python events in PyCareer'

    def items(self):
        return event_service.latest_events()[:settings.RSS_PAGE_SIZE]

    def item_title(self, item):
        return item['name']

    def item_description(self, item):
        return item['description']

    def item_link(self, item):
        return item['url']

    def item_pubdate(self, item):
        return item['created_at']

    def item_guid(self, item):
        return str(item['id'])
