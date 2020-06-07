import datetime
from django.contrib import admin
from .models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'lat', 'lon', 'location', 'country', 'start_date', 'end_date', 'calender_name', 'created_at', )
    ordering = ('-created_at', )
    list_filter = ('status', )
    readonly_fields = ('status', )
    actions = ('make_approved', 'make_declined', 'reindex_events')

    def _show_message(self, request, rows, message):
        if rows == 1:
            message_bit = "1 event was"
        else:
            message_bit = "%s events were" % rows
        self.message_user(request, "%s successfully marked as %s." % (message_bit, message))

    def make_approved(self, request, queryset):
        rows = queryset.update(status='approved')
        self._show_message(request, rows, 'approved')
    make_approved.short_description = 'Mark selected events as approved'

    def make_declined(self, request, queryset):
        rows = queryset.update(status='declined')
        self._show_message(request, rows, 'declined')
    make_declined.short_description = 'Mark selected events as declined'

    def reindex_events(self, request, queryset):
        total_rows = 0
        for row in queryset:
            row.modified_at = datetime.datetime.now()
            row.save()
            total_rows += 1
        self._show_message(request, total_rows, 'reindexed')
    reindex_events.short_description = 'Reindex selected events'

    def changelist_view(self, request, extra_context=None):
        if "HTTP_REFERER" in request.META:
            path = request.META['HTTP_REFERER'].split(request.path_info)

            if path[-1] and not path[-1].startswith('?'):
                if not request.GET.get('status__exact'):
                    q = request.GET.copy()
                    q['status__exact'] = 'pending'
                    request.GET = q
                    request.META['QUERY_STRING'] = request.GET.urlencode()

        return super(EventAdmin, self).changelist_view(request, extra_context=extra_context)


admin.site.register(Event, EventAdmin)
