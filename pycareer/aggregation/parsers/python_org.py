import urlparse
import urllib
from lxml import html, etree
import html2text

from pycareer import log
from. base import FeedParser, HTMPParser

logger = log.get_logger('parser')
WEBSITE_URL = 'https://www.python.org'


class PythonOrgFeedParser(FeedParser):
    def __init__(self):
        self.job_parser = PythonOrgJobParser()

    def parse(self, url=None):
        if not url:
            url = WEBSITE_URL + '/jobs/feed/rss/'

        feed_content = self.get_feed_content(url)
        for entry in feed_content['entries']:
            try:
                parse_result = urlparse.urlparse(entry['link'])
                netloc = parse_result.netloc
                if 'www' not in netloc:
                    netloc = 'www.' + netloc

                full_link = parse_result.scheme + '://' + netloc + parse_result.path
                content = self.job_parser.parse(full_link)
                yield content
            except StopIteration:
                raise
            except Exception:
                logger.exception('Exception while parsing %s' % url)


class PythonOrgJobListParser(HTMPParser):
    def __init__(self, paginate=True):
        self.job_parser = PythonOrgJobParser()
        self.paginate = paginate

    def _get_links(self, tree):
        links = tree.xpath('//ol/*/h2/span[@class="listing-company-name"]/a/@href')
        return links

    def _next_page(self, tree):
        next_page = tree.xpath('//ul[contains(@class, "pagination")]//li[@class="next"]/a')[0].attrib['href']
        return next_page

    def parse(self, url=None):
        if not url:
            url = WEBSITE_URL + '/jobs/'

        raw_content = self.get_raw_content(url)
        tree = html.fromstring(raw_content)
        for relative_link in self._get_links(tree):
            full_url = WEBSITE_URL + relative_link
            try:
                content = self.job_parser.parse(full_url)
                yield content
            except StopIteration:
                raise
            except Exception:
                logger.exception('Exception while parsing %s' % full_url)

        next_page = self._next_page(tree)
        if self.paginate and next_page:
            for content in self.parse(WEBSITE_URL + '/jobs/' + next_page):
                yield content


class PythonOrgJobParser(HTMPParser):
    def parse(self, url):
        logger.info('Starting to parse %s' % url)
        raw_content = self.get_raw_content(url)
        tree = html.fromstring(raw_content)
        job = self._construct_job(tree)
        job['provider_id'] = self._get_provider_id(url)
        job['provider_link'] = url
        return job

    def _construct_job(self, tree):
        location = self._get_location(tree).split(',')
        country_code = self._get_country_code(location[-1].strip())
        return {
            'title': self._get_title(tree),
            'description': self._get_description(tree),
            'country': country_code,
            'city': location[0].strip(),
            'state': location[1].strip() if len(location) == 3 else '',
            'published_at': self._get_published_at(tree),
            'company_name': self._get_company_name(tree),
            'contact_email': self._get_contact_email(tree),
            'contact_name': self._get_contact_name(tree),
            'contact_url': self._get_contact_url(tree)
        }

    def _get_provider_id(self, url):
        path = urlparse.urlparse(url).path
        id_ = path.split('/')[2]
        return "python.org-%s" % id_

    def _get_title(self, tree):
        return tree.xpath('//*/span[@class="company-name"]/text()')[0].strip()

    def _get_description(self, tree):
        elements = tree.xpath('//*/div[@class="job-description"]/*[position() > 2 and position() < last() - 1]')
        description = ''
        for elem in elements:
            description += etree.tostring(elem).strip()
        description = html2text.html2text(description)
        description = description.replace('&amp;', '&')
        return description

    def _get_location(self, tree):
        return tree.xpath('//*/span[@class="listing-location"]/a/text()')[0].strip()

    def _get_published_at(self, tree):
        time = tree.xpath('//*/span[@class="listing-posted"]/time')[0].attrib['datetime']
        return time

    def _get_company_name(self, tree):
        return tree.xpath('//*/h1//span[@class="company-name"]/text()[last()]')[0].strip()

    def _get_company_description(self, tree):
        xpath = '//*/div[@class="job-description"]/h2[text()="About the Company"]/following::p[1]/text()'
        description = tree.xpath(xpath)
        description = description[0].strip() if description else ''
        description = description.replace('&amp;', '&')
        return description

    def _get_contact_name(self, tree):
        elements = tree.xpath('//*/div[@class="job-description"]/ul[last()]/li[descendant::strong]')
        if len(elements) > 1:
            name = tree.xpath('//*/div[@class="job-description"]/ul[last()]/li[1]/text()')[0]
            return name.partition(':')[-1].strip()

    def _get_contact_email(self, tree):
        mailto = tree.xpath('(//*/div[@class="job-description"]/ul[last()]/*/a[starts-with(@href, "mailto")]/@href)')
        return urllib.unquote(mailto[0]).partition(':')[-1]

    def _get_contact_url(self, tree):
        url = tree.xpath('(//*/div[@class="job-description"]/ul[last()]/*/a[starts-with(@href, "http")]/@href)')
        return url[0] if url else ''

    def _get_country_code(self, raw_country):
        from pycareer.core.choices import COUNTRIES

        country_name = raw_country.upper()
        if country_name == 'UK':
            return 'GB'
        if len(country_name) == 2:
            return country_name
        elif country_name in ['USA', 'U.S.A', 'UNITED STATES OF AMERICA', 'THE UNITED STATES OF AMERICA']:
            return 'US'
        elif country_name == 'ENGLAND':
            return 'GB'
        elif country_name == 'THE NETHERLANDS':
            return 'NL'

        country_index = {c[1].upper(): c[0] for c in COUNTRIES}
        if country_name in country_index:
            return country_index[country_name]

        return country_name
