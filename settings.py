#################
##
## Momonitor Django Settings
##
#################


TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True

#Setup media path
import os
dir_path = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
MEDIA_ROOT = '%s/media/' % dir_path

#URLs. Probably want to serve these via a static http server, but here for DEBUG=True situations
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX = '/admin-media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'breadcrumbs.middleware.BreadcrumbsMiddleware',
)

ROOT_URLCONF = 'momonitor.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.admin',
    'south',
    'main',
    'slideshow',
    'mobile',
    'breadcrumbs',
    'social_auth'
)

#Redis Cache required to keep application state.
CACHES = {
    "default": {
        "BACKEND": "redis_cache.cache.RedisCache",
        "LOCATION": "127.0.0.1:6379:1",
        "OPTIONS": {
            "CLIENT_CLASS": "redis_cache.client.DefaultClient",
        }
    }
}

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.tz",
                               "django.contrib.messages.context_processors.messages",
                               'django.core.context_processors.request',
                               'momonitor.main.context_processors.service_endpoints')

#Email the admins if momonitor ever breaks
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

#This is the global endpoint that pagerduty uses for custom events.
PAGERDUTY_ENDPOINT = "https://events.pagerduty.com/generic/2010-04-15/create_event.json"
LOGIN_URL = '/social_auth/login/google/'

#Add media to the python path so that we can run code checks in the media/uploaded_scripts directory
import sys
sys.path.insert(0,os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'media')))

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.google.GoogleBackend',
    'django.contrib.auth.backends.ModelBackend'
)

FAKE_APP_PORT = 5000
FAKE_APP_HOST = "localhost"

IS_TESTING = sys.argv[1:2] == ['test']

if IS_TESTING:
    UMPIRE_ENDPOINT = "http://%s:%s/check" % (FAKE_APP_HOST,FAKE_APP_PORT)
    SENSU_API_ENDPOINT = "http://%s:%s" % (FAKE_APP_HOST,FAKE_APP_PORT)
    GRAPHITE_ENDPOINT = "http://%s:%s" % (FAKE_APP_HOST,FAKE_APP_PORT)
else:
    UMPIRE_ENDPOINT = ""
    SENSU_API_ENDPOINT = ""
    GRAPHITE_ENDPOINT = ""

#OAuth rule. Only allow people with a google email ending in 'example.org' to access the site
GOOGLE_WHITE_LISTED_DOMAINS = ['example.org']

# Set this to the Domain of the site that will be hosting momonitor.
# This will be used to create links in emails sent from momonitor. 
# Use 'http://localhost' for testing
DOMAIN = "" 
