DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

FAKE_APP_PORT = 5000
FAKE_APP_HOST = "localhost"

import sys
IS_TESTING = sys.argv[1:2] == ['test']

if IS_TESTING:
    UMPIRE_ENDPOINT = "http://%s:%s/check" % (FAKE_APP_HOST,FAKE_APP_PORT)
    SENSU_API_ENDPOINT = "http://%s:%s" % (FAKE_APP_HOST,FAKE_APP_PORT)
    GRAPHITE_ENDPOINT = "http://%s:%s" % (FAKE_APP_HOST,FAKE_APP_PORT)
else:
    UMPIRE_ENDPOINT = "http://example.org/check"
    SENSU_API_ENDPOINT = "http://example.org:4567"
    GRAPHITE_ENDPOINT = "http://example.org"

#OAuth rule. Only allow people with a google email ending in 'example.org' to access the site
GOOGLE_WHITE_LISTED_DOMAINS = ['example.org']

# Set this to the Domain of the site that will be hosting momonitor
DOMAIN = "http://localhost" 
