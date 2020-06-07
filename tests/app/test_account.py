import unittest

from mock import MagicMock, patch
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied

from pycareer.services.utils import get_uuid
from pycareer.account.models import Profile
from pycareer.account.decorators import recruiter_only


class TestProfileModel(unittest.TestCase):
    def setUp(self):
        self.objects = []
        user1 = User.objects.create(username=get_uuid())
        user2 = User.objects.create(username=get_uuid())
        self.dev_profile = Profile.objects.create(user=user1, type='developer')
        self.emp_profile = Profile.objects.create(user=user2, type='recruiter')
        self.objects.append(user1)
        self.objects.append(user2)
        self.objects.append(self.dev_profile)
        self.objects.append(self.emp_profile)

    def tearDown(self):
        for obj in self.objects:
            obj.delete()

    def test_is_recruiter(self):
        self.assertEqual(self.dev_profile.is_recruiter(), False)
        self.assertEqual(self.emp_profile.is_recruiter(), True)


class TestRecruiterOnlyDecorator(unittest.TestCase):
    """ Took help from this resource
        http://tech.novapost.fr/django-testing-view-decorators-en.html
    """
    def setUp(self):
        self.request = MagicMock()
        self.request.user.is_authenticated = MagicMock()
        self.request.user.profile.is_recruiter = MagicMock()
        self.view_func = MagicMock()

    def run_decorated_view(self, is_authenticated=True, is_recruiter=True):
        """Setup, decorate and call view, then return response."""
        self.request.user.is_authenticated.return_value = is_authenticated
        self.request.user.profile.is_recruiter.return_value = is_recruiter
        decorated_view = recruiter_only(self.view_func)

        return decorated_view(self.request)

    @patch('django.contrib.auth.views.redirect_to_login')
    def test_unauthorized(self, login_view_mock):
        self.run_decorated_view(is_authenticated=False)
        self.assertTrue(login_view_mock.called)
        self.assertFalse(self.view_func.called)

    def test_forbidden(self):
        self.assertRaises(PermissionDenied, self.run_decorated_view, True, False)

    def test_recruiter_only(self):
        self.run_decorated_view(is_authenticated=True)
        self.assertTrue(self.view_func.called)
