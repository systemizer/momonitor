from django.conf.urls.defaults import *
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.decorators import login_required
from django.views.static import serve
from django.conf import settings

urlpatterns = patterns('',
                       url('', include('momonitor.main.urls',namespace="main")),
                       url('^social_auth/', include('social_auth.urls')),
                       url('^mobile/', include('momonitor.mobile.urls',namespace="mobile")),
                       url('^slideshow/', include('momonitor.slideshow.urls',namespace="slideshow")),
                       url(r'^media/(?P<path>.*)$', login_required(serve), {
            'document_root': settings.MEDIA_ROOT}),
                       )

urlpatterns += staticfiles_urlpatterns()
