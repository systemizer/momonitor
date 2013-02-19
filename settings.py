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
    'breadcrumbs',
    'gunicorn',
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
                               'django.core.context_processors.request')

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

#Hackish way to set a TESTING variable. Currently this is only used so OAuth can be bypassed during testing.
TESTING = sys.argv[1:2] == ['test']

#Attempt to import local_settings
try:
    from local_settings import *
except:
    import sys
    print "Could not find local_settings.py. Exiting"
    sys.exit()


