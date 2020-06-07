from django.db import models
from django.contrib.auth.models import User

from pycareer.core.choices import COUNTRIES, USER_TYPE_CHOICES


class Skill(models.Model):
    name = models.CharField(max_length=35)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    type = models.CharField(max_length=15, choices=USER_TYPE_CHOICES)
    company_name = models.CharField(max_length=50, blank=True, null=True)
    company_description = models.TextField(blank=True)
    # developer profile
    title = models.CharField(max_length=100, blank=True, null=True)
    skills = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=15, blank=True, null=True)
    country = models.CharField(max_length=2, choices=COUNTRIES, blank=True, null=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    avatar_url = models.URLField(max_length=250, blank=True, null=True)
    linkedin_url = models.URLField(max_length=250, blank=True, null=True)
    github_url = models.URLField(max_length=250, blank=True, null=True)
    stackoverflow_url = models.URLField(max_length=250, blank=True, null=True)
    # Others
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profile'

    def __unicode__(self):
        return u'%s - %s' % (self.user.get_full_name(), self.type)

    def is_recruiter(self):
        return self.type == 'recruiter'

    def is_developer(self):
        return self.type == 'developer'


class Subscription(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    active = models.BooleanField(default=True)
    subscribe_at = models.DateTimeField(auto_now_add=True)
    unsubscribe_at = models.DateTimeField(null=True, editable=False)

    class Meta:
        db_table = 'subscription'

    def __unicode__(self):
        return self.email
