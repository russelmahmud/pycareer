import datetime as dt
from marshmallow import Schema, fields
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User

from pycareer import log
from pycareer.event.models import Event
from .base import Service
from .errors import NotFoundError
from .utils import validate


logger = log.get_logger('service')
today = dt.date.today()


class EventCreateSchema(Schema):
    name = fields.Str(required=True)
    start_date = fields.Str(required=True)
    end_date = fields.Str(required=True)
    city = fields.Str(allow_none=True)
    state = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    topics = fields.Str(allow_none=True)
    website = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    calender_link = fields.Str(allow_none=True)
    calender_name = fields.Str(allow_none=True)
    location = fields.Str(allow_none=True)
    lat = fields.Float(allow_none=True)
    lon = fields.Float(allow_none=True)
    provider_id = fields.Str(allow_none=True)
    submitted_by = fields.Integer(required=True)

    class Meta:
        strict = True


class EventService(Service):
    def __init__(self):
        self.model_class = Event

    def get(self, id_):
        event = self._get(id_)
        return event.to_dict()

    def create(self, data):
        validated_fields = validate(EventCreateSchema(), data)
        validated_fields['submitted_by'] = User.objects.get(id=validated_fields['submitted_by'])
        try:
            new_event = self.model_class(**validated_fields)
            new_event.save()
        except Exception:
            logger.exception('Exception while creating a event.')
            raise

        return new_event.to_dict()

    def create_or_update(self, provider_id, event_fields):
        event = self._get_by_provider_id(provider_id)
        if event is None:
            new_event = self.create(event_fields)
            self.publish_event(new_event)
            return new_event
        logger.info('Event already exists with provided_id : %s' % provider_id)
        return event.to_dict()

    def publish_event(self, event):
        event = self._get(event['id'])
        logger.info('Approving new event: %s', event.id)
        if event.lat and event.lon:
            event.status = 'approved'
            event.save()
            logger.info('Approved the event: %s', event.id)
        else:
            logger.info('Failed to approve the event: %s', event.id)

    def update(self, id_, data):
        raise NotImplementedError

    def delete(self, id_):
        event = self._get(id_)
        event.delete()

    def active_events(self):
        events = self.model_class.objects.filter(status='approved', end_date__gte=today)
        events_list = [e.to_dict() for e in events]
        # sorted_events = sorted(events_list, key=lambda k: k['start_date'])
        return events_list

    def past_events(self):
        two_month_before = today - dt.timedelta(days=180)
        events = self.model_class.objects.filter(status='approved',
                                                 end_date__gt=two_month_before,
                                                 end_date__lt=today).order_by('-end_date')
        return [e.to_dict() for e in events]

    def latest_events(self, offset=0, limit=None):
        events = self.model_class.objects.filter(status='approved').order_by('-created_at')
        events = events[offset:limit] if limit else events[offset:]
        return [e.to_dict() for e in events]

    def upcoming_events(self, offset=0, limit=None, event_type=None):
        events = self.model_class.objects.filter(start_date__gte=today).order_by('start_date')
        if event_type:
            events = events.filter(calender_name=event_type)
        events = events[offset:limit] if limit else events[offset:]
        return [e.to_dict() for e in events]

    def is_archived(self, id_):
        event = self._get(id_)
        return event.end_date < today

    def _get(self, id_):
        try:
            event = self.model_class.objects.get(id=id_)
        except ObjectDoesNotExist:
            message = 'Event id %s does not exist.' % id_
            logger.info(message)
            raise NotFoundError(message)

        return event

    def _get_by_provider_id(self, provider_id):
        try:
            event = self.model_class.objects.get(provider_id=provider_id)
        except ObjectDoesNotExist:
            event = None

        return event
