import os
import unittest
from urllib2 import URLError
from mock import patch

from pycareer.services import get_service


class TestIndeedService(unittest.TestCase):
    def setUp(self):
        self.service = get_service('indeed')
        self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.indeed_resp_file = os.path.join(self.data_dir, 'indeed_resp.json')

    def test_defaults(self):
        self.assertDictEqual(self.service.defaults, {
            'v': self.service.api_version,
            'publisher': self.service.publisher_key,
            'limit': self.service.page_size,
            'format': 'json',
            'chnl': 'PyCareer'
        })

    @patch('pycareer.core.requests.get', side_effect=URLError('DownloadError'))
    @patch('django.core.cache.cache.set')
    @patch('django.core.cache.cache.get')
    def test_search_exception(self, cache_get, cache_set, mock_search):
        cache_get.return_value = None
        results = self.service.search('python')
        self.assertEqual(results['num_found'], 0)
        self.assertEqual(len(results['items']), 0)
        mock_search.assert_called_once_with('http://api.indeed.com/ads/apisearch?publisher=7839952008968848&format=json&l=&chnl=PyCareer&q=python&start=0&limit=15&v=2')

    @patch('pycareer.core.requests.get')
    @patch('django.core.cache.cache.set')
    @patch('django.core.cache.cache.get')
    def test_search_resp_format(self, cache_get, cache_set, mock_search):
        cache_get.return_value = None
        with open(self.indeed_resp_file) as fp:
            mock_search.return_value = fp.read()

        results = self.service.search('python')
        self.assertEqual(results['num_found'], 841)
        self.assertEqual(len(results['items']), 2)
        job = results['items'][0]

        test_datasets = (
            ('title', 'Backend Web Developer - Python/Flask'),
            ('snippet', 'Taste for simplicity and elegance in technical design and implementation as well as an appreciation for test driven development and building software the right...'),
            ('company', 'Ihiji'),
            ('location', 'Austin, TX, US'),
            ('relative_time', '30+ days ago'),
            ('url', 'http://www.indeed.com/viewjob?jk=1f60d18a1c7719c1&qd=CvZ9rarVh7v9cVpo6xH_xnVjs7q5YQBT7Cf1rvXBeKZCclR6ryieTjX2r73ImtIsyrslan2223fS2pqXVjosGQfy244Lip7R7E4xVNTI8p8&indpubnum=7839952008968848&atk=1abp91udlbqnq9s3'),
        )
        for field, expected_out in test_datasets:
            self.assertEqual(job[field], expected_out)
