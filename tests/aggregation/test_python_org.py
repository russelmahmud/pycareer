import os
import re
import unittest

import httpretty

from pycareer.aggregation.parsers.python_org import PythonOrgFeedParser, PythonOrgJobListParser

JOB_DATA = {
    'title': 'Python Developer',
    'city': 'Boston',
    'state': 'MA',
    'country': 'US',
    'published_at': '2015-08-28T13:29:37.553066+00:00',
    'company_name': 'Kitewheel',
    'contact_email': 'careers@kitewheel.com',
    'contact_name': 'Jean Gaughan',
    'contact_url': '',
    'provider_id': 'python.org-618',
    'provider_link': 'https://www.python.org/jobs/618/',
}


class TestPythonOrg(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.feed_url = 'https://www.python.org/jobs/feed/rss/'
        cls.listing_page = 'https://www.python.org/jobs/'
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
        cls.test_job_details_file_name = 'python_org_job_details.html'
        cls.job_details_file = open(os.path.join(cls.test_data_dir, cls.test_job_details_file_name))
        cls.job_details = cls.job_details_file.read()

    @classmethod
    def tearDownClass(cls):
        cls.job_details_file.close()

    def register_details_page_call(self):
        url = 'python.org/jobs/' + '(?P<job_id>\d+)/$'
        httpretty.register_uri(method=httpretty.GET, uri=re.compile(url), status=200,
                               content_type='text/html', body=self.job_details)

    def validate_single_item(self, item):
        for key in JOB_DATA.keys():
            self.assertEqual(
                JOB_DATA[key],
                item[key],
                msg='Job %s does not match, Expected: %s, Actual: %s' % (key, JOB_DATA[key], item[key])
            )


@httpretty.activate
class TestPythonOrgFeedParser(TestPythonOrg):
    def setUp(self):
        self.test_feed_file_name = 'python_org_feed.txt'
        self.parser = PythonOrgFeedParser()

    def test_parse(self):
        with open(os.path.join(self.test_data_dir, self.test_feed_file_name)) as feed_file:
            content = feed_file.read()
            httpretty.register_uri(method=httpretty.GET, uri=self.feed_url, status=200,
                                   content_type='application/rss+xml',
                                   body=content)
            self.register_details_page_call()

            content = self.parser.parse(self.feed_url)
            items = list(content)
            self.assertEqual(len(items), 20)
            self.validate_single_item(items[0])


@httpretty.activate
class TestPythonOrgJobListParser(TestPythonOrg):
    def setUp(self):
        self.test_list_page_file = 'python_org_job_list.html'
        self.parser = PythonOrgJobListParser(paginate=False)

    def test_parse(self):
        with open(os.path.join(self.test_data_dir, self.test_list_page_file)) as list_page_file:
            content = list_page_file.read()
            httpretty.register_uri(method=httpretty.GET, uri=self.listing_page, status=200,
                                   content_type='text/html', body=content)
            self.register_details_page_call()
            content = self.parser.parse(self.listing_page)
            items = list(content)
            self.assertEqual(len(items), 25)
            self.validate_single_item(items[0])
