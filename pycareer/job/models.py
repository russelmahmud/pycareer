from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse

from pycareer.core.choices import COUNTRIES


PENDING = 'pending'
APPROVED = 'approved'
DECLINED = 'declined'
ARCHIVED = 'archived'

JOB_STATUS = (
    (PENDING, 'Pending'),
    (APPROVED, 'Approved'),
    (DECLINED, 'Declined'),
    (ARCHIVED, 'Archived')
)


class Job(models.Model):
    status = models.CharField(max_length=15, choices=JOB_STATUS, default=PENDING)
    # Job information
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    will_sponsor = models.BooleanField(default=False)
    visas = models.CharField(max_length=255, blank=True, null=True)
    # location
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=2, choices=COUNTRIES)
    published_at = models.DateTimeField(blank=True, null=True)
    # company information
    company_name = models.CharField(max_length=50)
    company_description = models.TextField(blank=True, null=True)
    contact_email = models.CharField(max_length=75)
    contact_name = models.CharField(max_length=50, blank=True, null=True)
    contact_url = models.CharField(max_length=255, blank=True, null=True)
    # source information
    provider_id = models.CharField(max_length=32, blank=True, null=True)
    provider_link = models.CharField(max_length=255, blank=True, null=True)
    # Others
    submitted_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'job'

    def __unicode__(self):
        return u'%s - %s' % (self.id, self.title)

    @staticmethod
    def location(city, state, country):
        if state:
            return u'%s, %s, %s' % (city, state, country)
        return u'%s, %s' % (city, country)

    @staticmethod
    def get_full_url(id_, title):
        kwargs = {
            'id_': id_,
            'slug': slugify(title),
        }
        return reverse('job_details',  kwargs=kwargs)

    def to_dict(self):
        excluding_fields = ['modified_at', 'submitted_by']
        job = {}
        for field in self._meta.fields:
            if field.name in excluding_fields:
                continue
            job[field.name] = getattr(self, field.name)

        job['published_at'] = self.published_at or self.created_at
        job['location'] = self.location(self.city, self.state, self.get_country_display())
        job['url'] = self.get_full_url(self.id, self.title)
        job['submitted_by'] = self.submitted_by.id
        return job


class Feed(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    parser = models.CharField(max_length=30)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'feed'

    def __unicode__(self):
        return u'%s' % self.name
