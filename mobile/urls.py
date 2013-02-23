from django.conf.urls.defaults import *

urlpatterns = patterns('momonitor.mobile.views',
                       url('^$', 'index',name="mobile_index"),
                       url('^service/(?P<service_id>.*)/$','service',name="service"),                       
                       url('^check/(?P<check_name>.*)/(?P<check_id>.*)/$','check',name="check"),                       
                       )
