import feedparser

from pycareer.core import requests


class BaseParser(object):
    def parse(self, url):
        """ It should return a list of items """
        raise NotImplementedError


class FeedParser(BaseParser):
    @classmethod
    def get_feed_content(cls, feed_url):
        return feedparser.parse(feed_url)


class HTMPParser(BaseParser):
    @classmethod
    def get_raw_content(cls, url):
        html = requests.get(url)
        return html
