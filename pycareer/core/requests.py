import urllib2
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch_errors import DownloadError


def get(url):
    try:
        result = urlfetch.fetch(url, method=urlfetch.GET, deadline=30)
    except DownloadError, e:
        raise urllib2.URLError(e.message)
    return result.content
