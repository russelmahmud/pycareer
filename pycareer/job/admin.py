from django.contrib import admin

from pycareer import tasks
from .models import Job, Feed, APPROVED, DECLINED, PENDING


class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'show_source', 'status', 'city', 'state', 'country',
                    'company_name', 'will_sponsor', 'published_at', 'created_at', 'show_preview')
    readonly_fields = ('status', 'provider_id', )
    actions = ('make_approved', 'make_declined', )
    ordering = ('-created_at', )
    list_filter = ('status', 'will_sponsor', )
    fieldsets = (
        ('Admin', {
            'fields': ('status', 'submitted_by', )
        }),
        ('Job Details', {
            'fields': ('title', 'city', 'state', 'country', 'published_at', 'description', 'will_sponsor', 'visas', )
        }),
        ('Company Information', {
            'fields': ('company_name', 'company_description', 'contact_name', 'contact_email', 'contact_url', )
        }),
        ('Source Information', {
            'fields': ('provider_id', 'provider_link', )
        }),
    )

    def show_source(self, obj):
        return '<a href="%s" target="_blank">%s</a>' % (obj.provider_link, obj.provider_id)
    show_source.allow_tags = True
    show_source.short_description = 'Source'

    def show_preview(self, obj):
        return '<a href="%s" target="_blank">%s</a>' % (obj.get_full_url(obj.id, obj.title), 'Preview')
    show_preview.allow_tags = True
    show_preview.short_description = 'Preview'

    def _show_message(self, request, rows, message):
        if rows == 1:
            message_bit = "1 job was"
        else:
            message_bit = "%s jobs were" % rows
        self.message_user(request, "%s successfully marked as %s." % (message_bit, message))

    def make_approved(self, request, queryset):
        job_ids = [job.id for job in queryset]
        rows = queryset.update(status=APPROVED)
        queryset.filter(published_at__isnull=True).update(published_at=datetime.now())
        tasks.job_approval_post_actions(job_ids)
        self._show_message(request, rows, 'approved')
    make_approved.short_description = 'Mark selected jobs as approved'

    def make_declined(self, request, queryset):
        rows = queryset.update(status=DECLINED)
        self._show_message(request, rows, 'declined')
    make_declined.short_description = 'Mark selected jobs as declined'

    def changelist_view(self, request, extra_context=None):
        if "HTTP_REFERER" in request.META:
            path = request.META['HTTP_REFERER'].split(request.path_info)

            if path[-1] and not path[-1].startswith('?'):
                if not request.GET.get('status__exact'):
                    q = request.GET.copy()
                    q['status__exact'] = PENDING
                    request.GET = q
                    request.META['QUERY_STRING'] = request.GET.urlencode()

        return super(JobAdmin, self).changelist_view(request, extra_context=extra_context)

admin.site.register(Job, JobAdmin)


class FeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'parser', 'active', 'modified_at', 'created_at')

admin.site.register(Feed, FeedAdmin)
