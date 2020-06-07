import datetime

from django.contrib.auth.models import User
from django.conf import settings
from googleapiclient.discovery import build
from oauth2client.client import AccessTokenRefreshError
import geopy.geocoders
from geopy.geocoders import Nominatim, GoogleV3
from lxml import html

from pycareer import log
from pycareer.services import get_service
from .parsers import get_parser
from .exceptions import ParserError

logger = log.get_logger('parser')
job_service = get_service('job')
event_service = get_service('event')

geopy.geocoders.options.default_user_agent = 'pycareer/1.2'
geopy.geocoders.options.default_timeout = 15
google = GoogleV3(api_key='')
nom = Nominatim()
geocache = {}


class Aggregator(object):
    @classmethod
    def aggregate(cls, parser_name):
        raise NotImplementedError

    @classmethod
    def _get_parser(cls, parser_name):
        return get_parser(parser_name)

    @classmethod
    def _get_user(cls):
        user, _ = User.objects.get_or_create(
            username=settings.AGGREGATOR_USER_EMAIL,
            email=settings.AGGREGATOR_USER_EMAIL
        )
        return user


class JobAggregator(Aggregator):
    @classmethod
    def aggregate(cls, parser_name):
        parser = cls._get_parser(parser_name)
        try:
            parsed_jobs = parser.parse()
        except Exception as e:
            logger.exception('Failed to parse the feed : %s' % parser_name)
            raise ParserError(e.message)

        for job in parsed_jobs:
            logger.info('Starting to save the job %s' % job['provider_id'])
            try:
                job['submitted_by'] = cls._get_user().id
                job['will_sponsor'] = False
                job_service.create_or_update(job['provider_id'], job)
            except Exception:
                logger.exception('Failed to save the job %s' % job['provider_id'])


class EventExtractor(object):
    def __init__(self):
        self.service = self._get_service(settings.GOOGLE_API_KEY)
        user, _ = User.objects.get_or_create(
            username=settings.AGGREGATOR_USER_EMAIL,
            email=settings.AGGREGATOR_USER_EMAIL
        )
        self.user = user

    def extract(self, cal_id, cal_name, singleEvents='False'):
        for event in self.calender_events(cal_id, singleEvents):
            item = self._event_to_item(event)
            item['calender_name'] = cal_name
            item['submitted_by'] = self.user.id

            logger.info('Starting to save the event %s' % item['provider_id'])
            try:
                event_service.create_or_update(item['provider_id'], item)
            except Exception:
                logger.exception('Failed to save the event %s' % item['provider_id'])


    def calender_events(self, cal_id, singleEvents='False'):
        # Today: only events present and future, we aggregate always for
        # last 1 day for recovering failure cases
        today = datetime.datetime.now()
        agoDay = today - datetime.timedelta(days=1)
        timeMin = agoDay.strftime('%Y-%m-%dT00:00:00.000Z')
        if singleEvents != 'False':
            timeMax = '{}-12-31T23:00:00.000Z'.format(datetime.datetime.now().year)
        else:
            timeMax = None
        #timeMin = datetime.datetime.now().isoformat()
        events = []

        try:
            page_token = None
            while True:
                event_list = self.service.events().list(
                    singleEvents=singleEvents, orderBy='startTime',calendarId=cal_id, pageToken=page_token, timeMin=timeMin, timeMax=timeMax
                ).execute()
                events.extend([event for event in event_list['items']])
                page_token = event_list.get('nextPageToken')
                if not page_token:
                    break
        except AccessTokenRefreshError:
            logger.error('The credentials have been revoked or expired, please re-run the application to re-authorize.')

        return events

    def _get_service(self, api_key):
        return build('calendar', 'v3', developerKey=api_key)

    def _event_to_item(self, event):
        item = {}
        item['name'] = event.get('summary')
        item['provider_id'] = event.get('id')

        item['start_date'] = event.get('start').get('date')
        if not item['start_date']:
            dateTime = event.get('start').get('dateTime')
            if dateTime:
                item['start_date'] = dateTime[:10]
        item['end_date'] = event.get('end').get('date')
        if not item['end_date']:
            dateTime = event.get('end').get('dateTime')
            if dateTime:
                item['end_date'] = dateTime[:10]

        item['website'] = self._get_website_url(event.get('description'))
        item['calender_link'] = event.get('htmlLink')
        item['month'] = self._get_month(item.get('start_date'))
        item['location'] = event.get('location')

        address = event.get('location')
        if address:
            location = self._geolocate(address)
            if location:
                lat, lon = location[0], location[1]
                item['lat'] = lat
                item['lon'] = lon
                latlon = "{},{}".format(lat, lon)
                country = self._loc_to_country(latlon)
                item['country'] = country
        return item

    def _get_website_url(self, description):
        tree = html.fromstring(description)
        elements = tree.xpath('//*/a')
        if len(elements) and elements[0] is not None:
            return elements[0].attrib['href']

    def _get_month(self, date_str):
        '''
        returns start month str from event
        '''
        return datetime.datetime.strptime(date_str[:10], '%Y-%m-%d').strftime("%B")

    def _geolocate(self, address):
        global geocache
        address = address.encode('utf-8')  # for storing in shelve
        loc = None
        if address not in geocache.keys():
            logger.info('Searching address in Google %s'  % address)
            try:
                loc = google.geocode(address)
            except:
                logger.info('Failed to fetch geocode from Google!')
                pass
            if not loc:
                logger.info('Searching address in Nominatim %s'  % address)
                try:
                    loc = nom.geocode(address)
                except:
                    logger.info('Failed to fetch geocode from Nominatim!')
                    pass
                if not loc:
                    new_address = ','.join(address.split(',')[1:])
                    logger.info('Researching address in Google %s'  % new_address)
                    try:
                        loc = google.geocode(new_address)
                    except:
                        logger.info('Failed to fetch geocode from Google again!')
                        pass
            if loc:
                loc = loc.latitude, loc.longitude, loc.raw
                geocache[address] = loc
        else:
            loc = geocache.get(address)[:2]
        return loc

    def _loc_to_country(self, latlon):
        global geocache
        if latlon not in geocache.keys():
            logger.info('Searching country of %s' % latlon)
            try:
                loc = nom.reverse(latlon, language='en')
                if loc:
                    country = loc.raw.get('address').get('country')
                    geocache[latlon] = country
                    return country
            except:
                return ''
        else:
            return geocache.get(latlon)
