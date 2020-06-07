from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.core.urlresolvers import reverse
from djangotoolbox.fields import BlobField

from pycareer.core.choices import COUNTRIES

PENDING = 'pending'
APPROVED = 'approved'
DECLINED = 'declined'
ARCHIVED = 'archived'

BOOK_STATUS = (
    (PENDING, 'Pending'),
    (APPROVED, 'Approved'),
    (DECLINED, 'Declined'),
    (ARCHIVED, 'Archived')
)

USER_LEVEL = (
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
)


class Category(models.Model):
    name = models.CharField(max_length=120)

    class Meta:
        db_table = 'book_categories'
        verbose_name_plural = 'categories'

    def __unicode__(self):
        return u'%s' % self.name


class Book(models.Model):
    status = models.CharField(max_length=15, choices=BOOK_STATUS, default='pending')
    # Book information
    category = models.ForeignKey(Category, null=True)
    title = models.CharField(max_length=255)
    provider_id = models.CharField(max_length=64, blank=True)
    description = models.TextField(blank=True)
    is_free = models.BooleanField(default=False)
    authors = models.CharField(max_length=512, blank=True)
    tags = models.CharField(max_length=255, blank=True)
    cover_url = models.URLField(max_length=255, blank=True)
    cover = BlobField(blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    user_level = models.CharField(max_length=32, choices=USER_LEVEL, blank=True)
    page_count = models.IntegerField(blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    amazon_link = models.URLField(max_length=255, blank=True)
    publisher_link = models.URLField(max_length=255, blank=True)
    book_format = models.CharField(max_length=32, blank=True)
    language = models.CharField(max_length=32, blank=True)
    isbn = models.CharField(max_length=15, blank=True)
    python2 = models.BooleanField(default=False)
    # Others
    amazon_rating = models.FloatField(null=True, blank=True)
    view_count = models.IntegerField(default=0)
    up_vote = models.IntegerField(default=0)
    submitted_by = models.ForeignKey(User)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'book'

    def __unicode__(self):
        return u'%s - %s' % (self.title, self.id)

    @property
    def url(self):
        return self.get_full_url(self.id, self.title)

    @staticmethod
    def get_full_url(id_, title):
        kwargs = {
            'id_': id_,
            'slug': slugify(title),
        }
        return reverse('book_details',  kwargs=kwargs)

    def to_dict(self):
        excluding_fields = ['modified_at', 'submitted_by', 'created_at']
        book = {}
        for field in self._meta.fields:
            if field.name in excluding_fields:
                continue
            book[field.name] = getattr(self, field.name)
        book['url'] = self.get_full_url(self.id, self.title)
        return book
