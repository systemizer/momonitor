from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = patterns('',
                       url('', include('momonitor.main.urls',namespace="main")),
                       url('^social_auth/', include('social_auth.urls')),
                       url('^mobile/', include('momonitor.mobile.urls',namespace="mobile")),
                       url('^slideshow/', include('momonitor.slideshow.urls',namespace="slideshow")),
                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT}),
                       )

urlpatterns += staticfiles_urlpatterns()
