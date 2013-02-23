from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

urlpatterns = patterns('',
                       url('', include('momonitor.main.urls')),
                       url('^social_auth/', include('social_auth.urls')),
                       url('^slideshow/', include('momonitor.slideshow.urls')),
                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT}),
                       )

urlpatterns += staticfiles_urlpatterns()
