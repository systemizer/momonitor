from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
                       url('', include('momonitor.main.urls')),
                       )

urlpatterns += staticfiles_urlpatterns()
