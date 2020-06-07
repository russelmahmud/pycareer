from pycareer.services.utils import get_uuid


def create_test_user(username=None, password=None, is_recruiter=False):
    from django.contrib.auth.models import User
    from pycareer.account.models import Profile

    username = username or get_uuid()
    password = password or get_uuid()
    email = username + '@test.com'
    objects = []

    try:
        user = User.objects.create_user(username, email=email, password=password)
        profile = Profile(user=user)
        profile.type = 'recruiter' if is_recruiter else 'developer'
        profile.save()
        objects.extend([user, profile])
    except:
        raise

    return user, objects


def create_test_job(submitted_by, **kwargs):
    from pycareer.job.models import Job

    try:
        job = Job(**kwargs)
        job.submitted_by = submitted_by
        job.save()
    except:
        raise

    return job
