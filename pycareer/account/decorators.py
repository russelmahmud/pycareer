from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test


def recruiter_only(view_func):
    """
    Decorator for views that checks that the user is logged in and is a recruiter,
    displaying the login page if necessary.
    """
    def _wrapped_view(request, *args, **kwargs):

        if not request.user.profile.is_recruiter():
            messages.warning(request, 'Please create a recruiter account to take this action.',
                             extra_tags='permission')
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    actual_decorator = user_passes_test(lambda u: u.is_authenticated())
    return actual_decorator(_wrapped_view)
