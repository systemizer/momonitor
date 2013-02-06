from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('',
                       url('', include('momonitor.main.urls')),
                       url('^social_auth/', include('social_auth.urls')),
                       )

urlpatterns += staticfiles_urlpatterns()
