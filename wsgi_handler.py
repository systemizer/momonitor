import sys
import os



sys.path.insert(0,os.path.normpath(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0,os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)) ,'..')))

import django.core.handlers.wsgi

os.environ['DJANGO_SETTINGS_MODULE'] = 'momonitor.settings'

application = django.core.handlers.wsgi.WSGIHandler()
