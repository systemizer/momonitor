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

#Optional (if you are using umpire checks)
UMPIRE_ENDPOINT = ""
GRAPHITE_ENDPOINT = ""

#By default, use GoogleBackend
AUTHENTICATION_BACKENDS = (
    'social_auth.backends.google.GoogleBackend',
)

#OAuth rule. Only allow people with a google email ending in 'example.org' to access the site
GOOGLE_WHITE_LISTED_DOMAINS = ['example.org']
DOMAIN = "http://localhost"
