import unittest
import random
import uuid
import datetime as dt
import pytest
from mock import patch
from django.contrib.auth.models import User
from django.conf import settings

from pycareer.job.models import Job, PENDING, APPROVED, ARCHIVED
from pycareer.services import get_service
from pycareer.services.errors import ValidationError, NotFoundError, IndexError
from pycareer.services.search.gae import GaeSearchEngine
from pycareer.services.search import JobSearch


today = dt.date.today()
tomorrow = today + dt.timedelta(days=1)


class TestJobService(unittest.TestCase):
    def setUp(self):
        self.job_ids = []
        self.service = get_service('job')
        self.test_user = User.objects.create_user(str(uuid.uuid1()))
        job_data = self._gen_job_data({
            'status': APPROVED,
            'submitted_by': self.test_user
        })
        self.test_job = Job.objects.create(**job_data)
        self._register_jobs(self.test_job.id)

    def tearDown(self):
        with patch.object(GaeSearchEngine, 'delete', return_value=None):
            for id_ in self.job_ids:
                self.service.delete(id_)
            self.test_user.delete()

    def _gen_job_data(self, overrides=None):
        job = {
            'title': 'Job title',
            'description': 'description',
            'city': 'City',
            'country': 'BD',
            'submitted_by': self.test_user.id,
            'company_name': 'Company Name',
            'contact_email': 'contact@email.com',
            'contact_name': 'Contact Name',
            'will_sponsor': False,
            'provider_id': str(uuid.uuid1()),
            'published_at': dt.datetime.now()
        }
        job.update(overrides or {})
        return job

    def _register_jobs(self, id_):
        self.job_ids.append(id_)

    def test_job_get_not_found(self):
        with self.assertRaises(NotFoundError):
            self.service.get(random.randint(100, 200))

    def test_job_get_success(self):
        job = self.service.get(self.test_job.id)
        self.assertEqual(job['id'], self.test_job.id)
        self.assertEqual(job['title'], self.test_job.title)

    def test_job_create_validation(self):
        with self.assertRaises(ValidationError):
            self.service.create({'title': 'Title'})

    def test_job_create_success(self):
        job_data = self._gen_job_data()
        new_job = self.service.create(job_data)
        self.assertEqual(new_job['title'], job_data['title'])
        self.assert_(new_job['id'] is not None)
        self.assertEqual(new_job['status'], PENDING)
        self._register_jobs(new_job['id'])

    def test_job_update_validation(self):
        with self.assertRaises(NotFoundError):
            self.service.update(random.randint(100, 200), {})

    def test_creation_of_create_or_update(self):
        job_data = self._gen_job_data()
        new_job = self.service.create_or_update(job_data['provider_id'], job_data)
        self.assertEqual(new_job['title'], job_data['title'])
        self.assert_(new_job['id'] is not None)
        self._register_jobs(new_job['id'])

    def test_should_not_update_job_for_status_approved(self):
        job_data = self._gen_job_data({'provider_id': self.test_job.provider_id})
        existing_job = self.service.create_or_update(job_data['provider_id'], job_data)
        self.assertNotEqual(existing_job['title'], 'Edited Title')
        self.assertEqual(job_data['provider_id'], existing_job['provider_id'])

    def test_should_update_job_for_status_pending(self):
        job_data = self._gen_job_data({
            'status': PENDING,
            'submitted_by': self.test_user
        })
        new_job = Job.objects.create(**job_data)
        self._register_jobs(new_job.id)
        job_data = self._gen_job_data({'provider_id': new_job.provider_id})
        job_data['title'] = 'Edited Title'
        existing_job = self.service.create_or_update(job_data['provider_id'], job_data)
        self.assertEqual(existing_job['title'], 'Edited Title')
        self.assertEqual(job_data['provider_id'], existing_job['provider_id'])

    def test_job_delete_not_found(self):
        with self.assertRaises(NotFoundError):
            self.service.delete(random.randint(100, 200))

    def test_job_delete_success(self):
        new_job = self.service.create(self._gen_job_data())
        job = self.service.get(new_job['id'])
        self.assertEqual(new_job['id'], job['id'])
        with patch.object(GaeSearchEngine, 'delete', return_value=None):
            self.service.delete(job['id'])
        with self.assertRaises(NotFoundError):
            self.service.get(job['id'])

    def test_active_jobs(self):
        job_data = self._gen_job_data({
            'status': APPROVED,
            'submitted_by': self.test_user
        })
        new_job = Job.objects.create(**job_data)
        resp = self.service.active_jobs(limit=2)
        self.assertEqual(resp['num_found'], 2)
        self.assertEqual(len(resp['items']), 2)
        self._register_jobs(new_job.id)

    def test_active_jobs_sorting(self):
        job_data = self._gen_job_data({
            'status': APPROVED,
            'submitted_by': self.test_user
        })
        new_job = Job.objects.create(**job_data)
        resp = self.service.active_jobs(limit=2)
        print resp['items']
        self.assertEqual(len(resp['items']), 2)
        self.assertEqual(resp['items'][0]['id'], new_job.id)
        self.assertEqual(resp['items'][1]['id'], self.test_job.id)
        self._register_jobs(new_job.id)

    def test_active_jobs_with_limit_param(self):
        job_data = self._gen_job_data({
            'status': APPROVED,
            'submitted_by': self.test_user
        })
        new_job = Job.objects.create(**job_data)
        resp = self.service.active_jobs(offset=1, limit=1)
        self.assertEqual(resp['num_found'], 2)
        self.assertEqual(len(resp['items']), 1)
        self._register_jobs(new_job.id)

    def test_latest_jobs_without_limit(self):
        job_data = self._gen_job_data({
            'status': APPROVED,
            'submitted_by': self.test_user
        })
        new_data = Job.objects.create(**job_data)
        jobs = self.service.latest_jobs()
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]['id'], new_data.id)
        self.assertEqual(jobs[1]['id'], self.test_job.id)
        self._register_jobs(new_data.id)

    def test_latest_jobs_with_limit(self):
        job_data = self._gen_job_data({
            'status': APPROVED,
            'submitted_by': self.test_user
        })
        new_data = Job.objects.create(**job_data)
        jobs = self.service.latest_jobs(limit=1)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['id'], new_data.id)
        self._register_jobs(new_data.id)

    @patch.object(GaeSearchEngine, 'delete', return_value=None)
    def test_archive_older_jobs(self, index_mock):
        job_data = self._gen_job_data({
            'status': APPROVED,
            'submitted_by': self.test_user,
            'published_at': today - dt.timedelta(settings.LISTING_VALID_DAYS + 1)
        })
        new_job = Job.objects.create(**job_data)
        self.assertEqual(new_job.status, APPROVED)
        self.service.archive_jobs()
        job = self.service.get(new_job.id)
        self.assertEqual(job['status'], ARCHIVED)
        assert index_mock.called
        self._register_jobs(new_job.id)

    def test_archive_not_latest_jobs(self):
        job_data = self._gen_job_data({
            'status': APPROVED,
            'submitted_by': self.test_user,
            'published_at': today - dt.timedelta(settings.LISTING_VALID_DAYS - 1)
        })
        new_job = Job.objects.create(**job_data)
        self.assertEqual(new_job.status, APPROVED)
        self.service.archive_jobs()
        job = self.service.get(new_job.id)
        self.assertEqual(job['status'], APPROVED)
        self._register_jobs(new_job.id)

    @patch.object(GaeSearchEngine, 'index', side_effect=IndexError('index error'))
    def test_index_job_exception(self, index_mock):
        with pytest.raises(IndexError) as excinfo:
            self.service.index(self.test_job.to_dict())
        assert excinfo.value.message == 'index error'
        assert index_mock.called

    @patch.object(GaeSearchEngine, 'index', return_value=None)
    def test_job_index(self, index_mock):
        job = self.test_job.to_dict()
        self.service.index(job)
        document = JobSearch.build_document(job)
        index_mock.assert_called_once_with(document)

    @patch.object(GaeSearchEngine, 'delete', side_effect=IndexError('index error'))
    def test_delete_index_exception_by_pass(self, index_mock):
        self.service.delete_index(self.test_job.id)
        assert index_mock.called

    @patch.object(GaeSearchEngine, 'delete', return_value=None)
    def test_single_job_delete_index(self, index_mock):
        self.service.delete_index(self.test_job.id)
        index_mock.assert_called_once_with([str(self.test_job.id)])
