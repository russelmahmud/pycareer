import hashlib
import uuid
import datetime
import json

from markdown import markdown
from lxml.html.clean import Cleaner
from django.utils.timesince import timesince
from marshmallow import ValidationError

from .errors import ValidationError as SValidation


def validate(schema, data):
    try:
        return schema.load(data).data
    except ValidationError as e:
        raise SValidation(e.message)


def sep_search_query(q):
    query, _, location = q.partition(',')
    return query, location


def convert_to_list(arg):
    """Converts arg to a list, empty if None, single element if not a list."""
    if isinstance(arg, basestring):
        return [arg]
    if arg is not None:
        try:
            return list(iter(arg))
        except TypeError:
            return [arg]
    return []


def get_relative_time(time):
    ago = timesince(time)
    return ago.split(",")[0] + " ago"


def create_snippet(text, start_index=0, max_chars=160):
    html = markdown(text)
    cleaner = Cleaner(allow_tags=[''],
                      kill_tags=['h2', 'h1', 'a'],
                      remove_unknown_tags=False)
    cleaned_text = cleaner.clean_html(html)
    return cleaned_text[start_index:max_chars] + ' ...'


def get_uuid():
    return hashlib.md5(str(uuid.uuid1())).hexdigest()


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        if isinstance(o, datetime.date):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)
