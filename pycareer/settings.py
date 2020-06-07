import os
from djangoappengine.settings_base import *
from django.contrib.messages import constants as message_constants
from djangoappengine.utils import on_production_server


IS_PRODUCTION = on_production_server
PROJECT_PATH = os.path.dirname(os.path.dirname(__file__))

# Activate django-dbindexer for the default database
DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}
AUTOLOAD_SITECONF = 'indexes'

SECRET_KEY = '=r-$b*8hglm+858&9t043hlm6-&6-3d3vfc4((7yd0dbrakhvi'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.messages',
    'django.contrib.markup',
    #'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'djangotoolbox',
    'autoload',
    'dbindexer',
    # Custom apps
    'pycareer.job',
    'pycareer.account',
    'pycareer.event',
    'pycareer.book',
    # djangoappengine should come last, so it can override a few manage.py commands
    'djangoappengine',
)

MIDDLEWARE_CLASSES = (
    # This loads the index definitions, so it has to come first
    'autoload.middleware.AutoloadMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'pycareer.core.context_processors.messages',
    'pycareer.core.context_processors.env_processor'
)

CACHES = {
    'default': {
        'BACKEND': 'pycareer.core.backends.GaeMemcachedCache',
    }
}

# This test runner captures stdout and associates tracebacks with their
# corresponding output. Helps a lot with print-debugging.
TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'

STATIC_ROOT = os.path.join(PROJECT_PATH, 'static')
STATIC_URL = '/static/'

TEMPLATE_DIRS = (os.path.join(PROJECT_PATH, 'templates'),)

ROOT_URLCONF = 'pycareer.urls'
if IS_PRODUCTION:
    DEBUG = False
    EMAIL_BACKEND = 'djangoappengine.mail.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MESSAGE_LEVEL = message_constants.INFO

# Contacts
ADMINS = ('admin@pycareer.com',)
SUPPORT_EMAIL = 'PyCareer Support <support@pycareer.com>'
NO_REPLY_EMAIL = 'PyCareer <noreply@pycareer.com>'
DEFAULT_EMAIL_SUBJECT = 'PyCareer'
DEFAULT_FROM_EMAIL = SUPPORT_EMAIL
AGGREGATOR_USER_EMAIL = 'aggregator@pycareer.com'

# Indeed.com
INDEED_SEARCH_PER_PAGE = 15

# Account
ACCOUNT_ACTIVATION_DAYS = 7
LOGIN_REDIRECT_URL = '/account/'
LOGIN_URL = '/account/login/'
AUTH_PROFILE_MODULE = 'account.Profile'

# Site
RSS_PAGE_SIZE = 10
LIST_PAGE_SIZE = 15
LISTING_VALID_DAYS = 365
GOOGLE_API_KEY = ''
