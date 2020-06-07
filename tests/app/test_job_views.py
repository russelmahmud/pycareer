import random

from django.core.urlresolvers import reverse
from django.test import Client
from django.test import TestCase
from mock import patch

from pycareer.services.email import EmailService
from pycareer.services.job import JobService
from .utils import create_test_user, create_test_job

# http://stackoverflow.com/questions/11885211/how-to-write-a-unit-test-for-a-django-view


class BaseTestCases(object):
    class JobBaseTest(TestCase):
        def setUp(self):
            self.client = Client()
            self.url = None
            self.template_name = None
            self.objects = []
            self.login_url = reverse('auth_login')
            self.employer, objs = create_test_user(password='test', is_recruiter=True)
            self.objects.extend(objs)
            self.developer, objs = create_test_user(password='test', is_recruiter=False)
            self.objects.extend(objs)

        def tearDown(self):
            for obj in self.objects:
                obj.delete()

        def test_authentication(self):
            response = self.client.get(self.url, follow=True)
            self.assertRedirects(response, self.login_url + '?next=' + self.url)
            response = self.client.post(self.url, follow=True)
            self.assertRedirects(response, self.login_url + '?next=' + self.url)

        def test_authorization_error(self):
            self.client.login(username=self.developer.username, password='test')
            response = self.client.get(self.url, follow=True)
            self.assertEqual(response.status_code, 403)
            self.assertTemplateUsed(response, '403.html')
            response = self.client.post(self.url, follow=True)
            self.assertEqual(response.status_code, 403)
            self.assertTemplateUsed(response, '403.html')

        def test_recruiter_account(self):
            self.client.login(username=self.employer.username, password='test')
            response = self.client.get(self.url, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, self.template_name)


class TestJobCreation(BaseTestCases.JobBaseTest):
    def setUp(self):
        super(TestJobCreation, self).setUp()
        self.url = reverse('job_post')
        self.template_name = 'job/create.html'

    def test_initial_data(self):
        self.client.login(username=self.employer.username, password='test')
        response = self.client.get(self.url, data={})
        self.assertEqual(response.context_data['form']['contact_email'].value(), self.employer.email)

    def test_form_validation_error(self):
        self.client.login(username=self.employer.username, password='test')
        response = self.client.post(self.url, data={})
        self.assertFormError(response, 'form', 'title', 'This field is required.')

    @patch.object(EmailService, 'send_support')
    def test_success_job_post(self, email_mock):
        self.client.login(username=self.employer.username, password='test')
        response = self.client.post(self.url, data=_create_job_data())
        self.assertTrue(email_mock.called)
        self.assertRedirects(response, self.client.session['job_url'])

    @patch.object(EmailService, 'send_support', side_effect=Exception('Boom'))
    def test_email_exception(self, email_mock):
        self.client.login(username=self.employer.username, password='test')
        response = self.client.post(self.url, data=_create_job_data())
        self.assertTrue(email_mock.called)
        self.assertRedirects(response, self.client.session['job_url'])


class TestJobUpdate(BaseTestCases.JobBaseTest):
    def setUp(self):
        super(TestJobUpdate, self).setUp()
        self.job = create_test_job(self.employer, **_create_job_data())
        self.objects.append(self.job)
        self.url = reverse('job_update', args=(self.job.id, ))
        self.template_name = 'job/update.html'

    def test_not_found(self):
        url = reverse('job_update', args=(random.randint(1000, 100000), ))
        self.client.login(username=self.employer.username, password='test')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_job_owner(self):
        employer_2, objs = create_test_user(password='test', is_recruiter=True)
        self.objects.extend(objs)
        self.client.login(username=employer_2.username, password='test')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')


class TestJobDelete(TestCase):
    def setUp(self):
        self.client = Client()
        self.objects = []
        self.login_url = reverse('auth_login')
        self.employer, objs = create_test_user(password='test', is_recruiter=True)
        self.objects.extend(objs)
        self.job = create_test_job(self.employer, **_create_job_data())
        self.objects.append(self.job)
        self.url = reverse('job_delete', args=(self.job.id, ))

    def tearDown(self):
        for obj in self.objects:
            obj.delete()

    def test_authentication(self):
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.login_url + '?next=' + self.url)

    def test_not_found(self):
        url = reverse('job_delete', args=(random.randint(1000, 100000), ))
        self.client.login(username=self.employer.username, password='test')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_job_owner(self):
        employer_2, objs = create_test_user(password='test', is_recruiter=True)
        self.objects.extend(objs)
        self.client.login(username=employer_2.username, password='test')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')

    @patch.object(JobService, 'delete')
    def test_can_not_delete_approved_job(self, mock_delete):
        job_data = _create_job_data()
        job_data['status'] = 'approved'
        job = create_test_job(self.employer, **job_data)
        self.objects.append(job)
        self.client.login(username=self.employer.username, password='test')
        url = reverse('job_delete', args=(job.id, ))
        response = self.client.get(url, follow=True)
        self.assertFalse(mock_delete.called)
        self.assertRedirects(response, reverse('jobs_mine'))

    @patch.object(JobService, 'delete')
    def test_delete_success(self, mock_delete):
        self.client.login(username=self.employer.username, password='test')
        response = self.client.get(self.url, follow=True)
        self.assertTrue(mock_delete.called)
        self.assertRedirects(response, reverse('jobs_mine'))


class TestJobArchive(TestCase):
    def setUp(self):
        self.client = Client()
        self.objects = []
        self.login_url = reverse('auth_login')
        self.employer, objs = create_test_user(password='test', is_recruiter=True)
        self.objects.extend(objs)
        self.job = create_test_job(self.employer, **_create_job_data())
        self.objects.append(self.job)
        self.url = reverse('job_archive', args=(self.job.id, ))

    def tearDown(self):
        for obj in self.objects:
            obj.delete()

    def test_authentication(self):
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, self.login_url + '?next=' + self.url)

    def test_not_found(self):
        url = reverse('job_archive', args=(random.randint(1000, 100000), ))
        self.client.login(username=self.employer.username, password='test')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')

    def test_job_owner(self):
        employer_2, objs = create_test_user(password='test', is_recruiter=True)
        self.objects.extend(objs)
        self.client.login(username=employer_2.username, password='test')
        response = self.client.get(self.url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')
        response = self.client.post(self.url, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertTemplateUsed(response, '403.html')

    @patch.object(JobService, 'archive')
    def test_can_not_archive_non_approved_job(self, mock_archive):
        self.client.login(username=self.employer.username, password='test')
        response = self.client.get(self.url, follow=True)
        self.assertFalse(mock_archive.called)
        self.assertRedirects(response, reverse('jobs_mine'))

    @patch.object(JobService, 'archive')
    def test_can_archive_approved_job_only(self, mock_archive):
        job_data = _create_job_data()
        job_data['status'] = 'approved'
        job = create_test_job(self.employer, **job_data)
        self.objects.append(job)
        self.client.login(username=self.employer.username, password='test')
        url = reverse('job_archive', args=(job.id, ))
        response = self.client.get(url, follow=True)
        self.assertTrue(mock_archive.called)
        self.assertRedirects(response, reverse('jobs_mine'))


class TestMyJobsView(BaseTestCases.JobBaseTest):
    def setUp(self):
        super(TestMyJobsView, self).setUp()
        self.job = create_test_job(self.employer, **_create_job_data())
        self.objects.append(self.job)
        self.url = reverse('jobs_mine')
        self.template_name = 'account/jobs.html'

    def test_my_jobs_list(self):
        job_data = _create_job_data()
        job = create_test_job(self.employer, **job_data)
        self.objects.append(job)
        self.client.login(username=self.employer.username, password='test')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data['jobs']), 2)


def _create_job_data():
    return {
        'company_name': 'Company',
        'title': 'Title',
        'city': 'City',
        'country': 'US',
        'description': 'Description',
        'will_sponsor': False,
        'contact_email': 'test@test.com'
    }
