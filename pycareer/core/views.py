from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.contrib import messages

from pycareer.job.models import Feed, Job
from pycareer.event.models import Event
from pycareer.book.models import Book, APPROVED
from pycareer.account.models import Skill, Subscription
from pycareer.services import get_service
from .forms import ContactForm, NewsletterForm


email_service = get_service('email')
job_service = get_service('job')
event_service = get_service('event')

def homepage(request):
    data = {
        'books': Book.objects.filter(status=APPROVED)[:6],
        'events': event_service.upcoming_events(limit=5),
        'jobs': job_service.latest_jobs(limit=5)
    }
    return render_to_response('home.html', data, context_instance=RequestContext(request))


class ContactView(FormView):
    form_class = ContactForm
    template_name = 'contact.html'

    def form_valid(self, form):
        email_service.send_support(subject='New Contact Form Submission',
                                   template='emails/contact_template.html',
                                   ctx=form.cleaned_data)

        messages.success(self.request, 'Thank you! Your message has been successfully sent.', extra_tags='contact')
        return super(ContactView, self).form_valid(form)

    def get_success_url(self):
        return reverse('contact_page')


class NewsletterView(FormView):
    form_class = NewsletterForm
    template_name = 'newsletter.html'

    def form_valid(self, form):
        Subscription.objects.get_or_create(
            email=form.cleaned_data['email'],
            defaults={
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name']
            }
        )
        messages.success(self.request, 'Thank you! You have subscribed the newsletter successfully.', extra_tags='newsletter')
        return super(NewsletterView, self).form_valid(form)

    def get_success_url(self):
        return reverse('newsletter_page')


def privacy(request):
    return render_to_response('privacy.html', context_instance=RequestContext(request))


def load_initial_data(request, deferred):
    try:
        User.objects.get(username='russel')
    except ObjectDoesNotExist:
        User.objects.create_superuser('russel', 'russel.081@gmail.com', 'russel')

    feeds = [{
        "name": "Python.org RSS",
        "description": "Python jobs from python.org RSS feed",
        "parser": "python_org_rss",
        "active": False}, {
        "name": "Python.org HTML",
        "description": "Python jobs from python.org website",
        "parser": "python_org_html",
        "active": False,
    }]

    for feed in feeds:
        try:
            Feed.objects.get(parser=feed['parser'])
        except ObjectDoesNotExist:
            f = Feed(**feed)
            f.save()

    skills = ['Python', 'Django']
    for skill in skills:
        try:
            Skill.objects.get(name=skill)
        except ObjectDoesNotExist:
            s = Skill(name=skill)
            s.save()

    return HttpResponse('Success')


def reindex_jobs(request, deferred):
    job_service = get_service('job')
    job_search = get_service('job_search')
    active_jobs = job_service.active_jobs()['items']
    job_search.delete_all_in_index()
    job_service.index_jobs([job['id'] for job in active_jobs])
    return HttpResponse('Success')
