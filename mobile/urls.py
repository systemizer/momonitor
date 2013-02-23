from django.conf.urls.defaults import *

urlpatterns = patterns('momonitor.mobile.views',
                       url('^$', 'index',name="mobile_index"),
                       )
