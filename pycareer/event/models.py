from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse

from pycareer.core.choices import COUNTRIES

EVENT_STATUS = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('declined', 'Declined')
)


class Event(models.Model):
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=15, choices=EVENT_STATUS, default='pending')
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(null=True, blank=True)
    topics = models.CharField(max_length=255, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    calender_link = models.URLField(blank=True, null=True)
    calender_name = models.CharField(max_length=100, blank=True, null=True)
    # location
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    # Others
    provider_id = models.CharField(max_length=64, blank=True, null=True)
    submitted_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'event'

    def __unicode__(self):
        return u'%s - %s' % (self.name, self.id)

    def get_absolute_url(self):
        kwargs = {
            'id_': self.id,
            'slug': self.slug,
        }
        return reverse('event_details',  kwargs=kwargs)

    @property
    def slug(self):
        return u'%s' % slugify(self.name)

    def to_dict(self):
        excluding_fields = ['modified_at', 'submitted_by', 'created_at']
        event = {}
        for field in self._meta.fields:
            if field.name in excluding_fields:
                continue
            event[field.name] = getattr(self, field.name)
        event['url'] = self.get_absolute_url()
        return event
