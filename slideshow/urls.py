from django.conf.urls.defaults import *

urlpatterns = patterns('momonitor.slideshow.views',
                       url('^$', 'index',name="index"),
                       url('^view/(?P<service_id>.*)/$', 'view_slideshow',name="view")
                       )
