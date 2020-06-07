import json
import urllib2
import urllib
import copy
import hashlib
from django.conf import settings
from django.core.cache import cache

from pycareer import log
from pycareer.core import requests
from .utils import sep_search_query, validate
from .schema.job import JobListResponse

logger = log.get_logger('service')

INDEED_PUBLISHER_KEY = getattr(settings, 'INDEED_PUBLISHER_KEY', '7839952008968848')
INDEED_SEARCH_PER_PAGE = getattr(settings, 'INDEED_SEARCH_PER_PAGE', 15)
INDEED_API_VERSION = getattr(settings, 'INDEED_API_VERSION', 2)
CACHE_EXPIRE = 24 * 60 * 60


class IndeedApi(object):
    def __init__(self):
        self.publisher_key = INDEED_PUBLISHER_KEY
        self.page_size = INDEED_SEARCH_PER_PAGE
        self.api_version = INDEED_API_VERSION
        self.base_url = 'http://api.indeed.com'

    @property
    def search_url(self):
        return self.base_url + '/ads/apisearch'

    @property
    def defaults(self):
        return {
            'v': self.api_version,
            'publisher': self.publisher_key,
            'limit': self.page_size,
            'format': 'json',
            'chnl': 'PyCareer'
        }

    @staticmethod
    def gen_key(key):
        m = hashlib.md5(key).hexdigest()
        return m

    def search(self, query, **kwargs):
        url = self._build_search_url(query, **kwargs)
        logger.info('Indeed : %s' % url)
        s_key = self.gen_key(url)
        api_response = cache.get(s_key)

        if not api_response:
            api_response = self._fetch(url)
            cache.set(s_key, api_response, CACHE_EXPIRE)

        json_resp = json.loads(api_response)

        return validate(JobListResponse(), {
            'num_found': json_resp['totalResults'],
            'items': json_resp['results']
        })

    def _build_search_url(self, q, **kwargs):
        query, location = sep_search_query(q)
        params = copy.copy(self.defaults)
        params.update({
            'l': location,
            'q': query,
            'limit': kwargs.pop('limit', self.page_size),
            'start': kwargs.pop('start', 0)
        })
        params.update(kwargs)
        return self.search_url + '?' + urllib.urlencode(params)

    def _fetch(self, url):
        try:
            api_response = requests.get(url)
        except urllib2.URLError:
            logger.exception('Indeed : Unable to fetch Indeed Jobs API.')
            api_response = '{"totalResults": 0, "results": []}'

        return api_response
