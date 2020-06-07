import unittest
import random
import datetime as dt
from django.contrib.auth.models import User

from pycareer.event.models import Event
from pycareer.services import get_service
from pycareer.services import ValidationError, NotFoundError


today = dt.date.today()
tomorrow = today + dt.timedelta(days=1)
yesterday = today - dt.timedelta(days=1)


class TestEventService(unittest.TestCase):
    def setUp(self):
        self.event_ids = []
        self.service = get_service('event')
        self.test_user = User.objects.create_user('Username %d' % random.randint(1, 100))
        event_data = self._gen_event_data({
            'status': 'approved',
            'submitted_by': self.test_user
        })
        self.test_event = Event.objects.create(**event_data)
        self._register_events(self.test_event.id)

    def tearDown(self):
        for id_ in self.event_ids:
            self.service.delete(id_)
        self.test_user.delete()

    def _gen_event_data(self, overrides=None):
        event = {
            'name': 'Name %d' % random.randint(1, 100),
            'start_date': yesterday - dt.timedelta(days=7),
            'end_date': yesterday,
            'city': 'City',
            'country': 'BD',
            'submitted_by': self.test_user.id,
            'month': 'January'
        }
        event.update(overrides or {})
        return event

    def _register_events(self, id_):
        self.event_ids.append(id_)

    def test_event_get_not_found(self):
        with self.assertRaises(NotFoundError):
            self.service.get(random.randint(100, 200))

    def test_event_get_success(self):
        event = self.service.get(self.test_event.id)
        self.assertEqual(event['id'], self.test_event.id)
        self.assertEqual(event['name'], self.test_event.name)

    def test_event_create_validation(self):
        with self.assertRaises(ValidationError):
            self.service.create({'name': 'Name'})

    def test_event_create_success(self):
        event_data = self._gen_event_data()
        new_event = self.service.create(event_data)
        self.assertEqual(new_event['name'], event_data['name'])
        self.assert_(new_event['id'] is not None)
        self.assertEqual(new_event['status'], 'pending')
        self._register_events(new_event['id'])

    def test_event_delete_not_found(self):
        with self.assertRaises(NotFoundError):
            self.service.delete(random.randint(100, 200))

    def test_event_delete_success(self):
        new_event = self.service.create(self._gen_event_data())
        event = self.service.get(new_event['id'])
        self.assertEqual(new_event['id'], event['id'])
        self.service.delete(event['id'])
        with self.assertRaises(NotFoundError):
            self.service.get(event['id'])

    def test_active_events(self):
        event_data = self._gen_event_data({
            'end_date': tomorrow,
            'status': 'approved',
            'submitted_by': self.test_user
        })
        new_event = Event.objects.create(**event_data)
        events = self.service.active_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['id'], new_event.id)
        self._register_events(new_event.id)

    def test_past_events(self):
        event_data = self._gen_event_data({
            'status': 'approved',
            'submitted_by': self.test_user,
            'end_date': yesterday - dt.timedelta(days=3)
        })
        new_event = Event.objects.create(**event_data)
        events = self.service.past_events()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['id'], self.test_event.id)
        self.assertEqual(events[1]['id'], new_event.id)
        self._register_events(new_event.id)

    def test_latest_events(self):
        event_data = self._gen_event_data({
            'status': 'approved',
            'submitted_by': self.test_user
        })
        new_event = Event.objects.create(**event_data)
        events = self.service.latest_events()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['id'], new_event.id)
        self.assertEqual(events[1]['id'], self.test_event.id)
        self._register_events(new_event.id)

    def test_is_archived_true(self):
        self.assertEqual(self.service.is_archived(self.test_event.id), True)

    def test_is_archived_false(self):
        event_data = self._gen_event_data({
            'end_date': tomorrow
        })
        new_event = self.service.create(event_data)
        self.assertEqual(self.service.is_archived(new_event['id']), False)
        self._register_events(new_event['id'])
