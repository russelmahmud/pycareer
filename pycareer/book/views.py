from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import Http404
from django.conf import settings
from django.db.models import Q
from django.core.paginator import Paginator

from pycareer import log
from pycareer.core.paginator import Paginator as CPaginator
from .models import Book, APPROVED

logger = log.get_logger()


def book_list(request):
    pagesize = settings.LIST_PAGE_SIZE + 3
    query = request.GET.get('q', '')
    page = CPaginator.validate_number(request.GET.get('page'))
    # offset = pagesize * (page - 1)
    books = Book.objects.filter(status=APPROVED).order_by('id')
    paginator = Paginator(books, pagesize)
    books = paginator.page(page)
    # if query:
    #     books = books.filter(tags__contains=query)
    # num_found = books.count()
    # books = books[offset:offset+pagesize]
    return render_to_response('book/list.html', {
        'title': 'Python Events',
        'books': books,
        'paginator': books
    }, context_instance=RequestContext(request))


def book_details(request, id_, slug):
    try:
        book = Book.objects.get(id=id_)
    except Book.DoesNotExist:
        raise Http404

    book.view_count = book.view_count + 1
    book.save()
    book.full_url = _build_full_url(request, book.url)
    book.tags = book.tags.split(',')
    related_books = Book.objects.filter(category=book.category, status=APPROVED).exclude(id=book.id)[:5]
    return render_to_response('book/details.html', {
        'book': book,
        'related_books': related_books
    }, context_instance=RequestContext(request))


def _build_full_url(request, path):
    return request.build_absolute_uri(path)
