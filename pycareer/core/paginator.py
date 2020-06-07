import math
from django.conf import settings


class Paginator(object):
    def __init__(self, page, total):
        self.per_page = settings.INDEED_SEARCH_PER_PAGE
        self.total = total
        num_pages = total / float(self.per_page)
        self.num_pages = int(math.ceil(num_pages))
        self.current_page = page

    @classmethod
    def validate_number(cls, number):
        """Validates the given 1-based page number."""
        try:
            number = int(number)
        except (TypeError, ValueError):
            return 1

        if number < 1:
            return 1

        return number

    def has_next(self):
        return self.current_page < self.num_pages

    def has_previous(self):
        return self.current_page > 1

    def has_other_pages(self):
        return self.has_previous() or self.has_next()

    def next_page_number(self):
        return self.current_page + 1

    def previous_page_number(self):
        return self.current_page - 1
