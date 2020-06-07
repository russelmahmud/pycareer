from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required

from .views import CustomRegistrationView, ProfileUpdateView, CustomActivationView, auto_complete_skills

urlpatterns = patterns(
    '',
    url(r'^register/$', CustomRegistrationView.as_view(), name='registration_register'),
    url(r'^activate/(?P<activation_key>\w+)/$', CustomActivationView.as_view(), name='registration_activate'),
    url(r'^password/change/$', 'pycareer.account.views.change_password', name='auth_password_change'),
    url(r'^password/reset/$', 'pycareer.account.views.reset_password', name='auth_password_reset'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        'pycareer.account.views.reset_password_confirm', name='auth_password_reset_confirm'),
    url(r'', include('registration.backends.default.urls')),
    url(r'^skill-autocomplete/$', auto_complete_skills, name='skills_autocomplete'),
    url(r'^profile/$', login_required(ProfileUpdateView.as_view()), name='profile_page'),
    url(r'^$', 'pycareer.account.views.my_account', name='account_page'),
)
