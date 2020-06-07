from django.contrib import admin
from django import forms
from django.shortcuts import render, redirect
from django.conf.urls import url
from django.http import HttpResponse
import xlrd
from numbers import Number

from pycareer.core.utils import XLSXSheet, xlsx_str_reader, xlsx_date_reader, xlsx_empty_int_reader
from .models import Book, Category, APPROVED, DECLINED, PENDING


class ExcelImportForm(forms.Form):
    excel_file = forms.FileField()


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'is_free', 'user_level', 'publisher', 'publication_date',
                    'amazon_rating', 'view_count', 'up_vote', 'created_at', 'show_preview')
    readonly_fields = ('status', 'view_count', 'up_vote', 'submitted_by')
    actions = ('make_approved', 'make_declined')
    ordering = ('-created_at', )
    list_filter = ('status', 'category', 'user_level', 'is_free', )
    exclude = ('submitted_by', )
    search_fields = ('isbn', )

    def get_urls(self):
        urls = super(BookAdmin, self).get_urls()
        my_urls = [
            url('import-books/', self.import_excel),
        ]
        return my_urls + urls

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.submitted_by = request.user
        super(BookAdmin, self).save_model(request, obj, form, change)

    def show_preview(self, obj):
        return '<a href="%s" target="_blank">%s</a>' % (obj.get_full_url(obj.id, obj.title), 'Preview')
    show_preview.allow_tags = True
    show_preview.short_description = 'Preview'

    def _show_message(self, request, rows, message):
        if rows == 1:
            message_bit = "1 book was"
        else:
            message_bit = "%s books were" % rows
        self.message_user(request, "%s successfully marked as %s." % (message_bit, message))

    def make_approved(self, request, queryset):
        book_ids = [book.id for book in queryset]
        rows = queryset.update(status=APPROVED)
        self._show_message(request, rows, 'approved')
    make_approved.short_description = 'Mark selected books as approved'

    def make_declined(self, request, queryset):
        rows = queryset.update(status=DECLINED)
        self._show_message(request, rows, 'declined')
    make_declined.short_description = 'Mark selected books as declined'

    def changelist_view(self, request, extra_context=None):
        if "HTTP_REFERER" in request.META:
            path = request.META['HTTP_REFERER'].split(request.path_info)

            if path[-1] and not path[-1].startswith('?'):
                if not request.GET.get('status__exact'):
                    q = request.GET.copy()
                    q['status__exact'] = PENDING
                    request.GET = q
                    request.META['QUERY_STRING'] = request.GET.urlencode()

        return super(BookAdmin, self).changelist_view(request, extra_context=extra_context)

    def import_excel(self, request):
        if request.method == 'POST':
            fp = request.FILES['excel_file']
            workbook = xlrd.open_workbook(file_contents=fp.read())
            sheet = XLSXSheet(workbook.sheets()[0])
            book_rows = []
            for row in sheet:
                book = self._transform_to_model_fields(row)
                book_rows.append(book)

            for row in book_rows:
                try:
                    b = Book.objects.get(isbn=row['isbn'])
                except Book.DoesNotExist:
                    b = Book()
                b.__dict__.update(row)
                b.submitted_by = request.user
                b.save()

            self.message_user(request, 'Your excel file has been imported')
            return redirect('..')
        form = ExcelImportForm()
        payload = {'form': form}
        return render(
            request, 'admin/book/excel_form.html', payload
        )

    def _transform_to_model_fields(self, row):
        mappings = {
            'CoverUrl': (xlsx_str_reader, 'cover_url'),
            'Title': (xlsx_str_reader, 'title'),
            'ProviderId': (xlsx_str_reader, 'provider_id'),
            'Description': (xlsx_str_reader, 'description'),
            'Authors': (xlsx_str_reader, 'authors'),
            'Format': (xlsx_str_reader, 'book_format'),
            'PageCount': (xlsx_empty_int_reader, 'page_count'),
            'Language': (xlsx_str_reader, 'language'),
            'Publisher': (xlsx_str_reader, 'publisher'),
            'Price': (float, 'price'),
            'PublicationDate': (xlsx_date_reader, 'publication_date'),
            'ISBN-13': (xlsx_str_reader, 'isbn'),
            'UserRating': (float, 'amazon_rating'),
            'AmazonBuyLink': (xlsx_str_reader, 'amazon_link'),
            'PublisherLink': (xlsx_str_reader, 'publisher_link'),
        }
        result = {}
        for column_name, value in row.items():
            if column_name not in mappings.keys():
                continue
            func, field = mappings[column_name]
            if isinstance(value, Number):
                result[field] = func(value)
            elif value:
                result[field] = func(value)
        return result


admin.site.register(Book, BookAdmin)
admin.site.register(Category, CategoryAdmin)
