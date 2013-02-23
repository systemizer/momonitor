from django.conf.urls.defaults import *

urlpatterns = patterns('momonitor.slideshow.views',
                       url('^$', 'index',name="main_index"),
                       url('^view/(?P<service_id>.*)/$', 'view_slideshow',name="main_slideshow")
                       )
