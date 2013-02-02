from django.conf.urls.defaults import *

urlpatterns = patterns('momonitor.main.views',
                       url('^$','index',name="main_index"),
                       url('^service/(?P<service_id>.*)/$','service',name="main_service"),
                       url('^refresh/service/(?P<service_id>.*)/$','refresh_service',name="main_refresh_service"),
                       url('^delete/service-check/(?P<service_check_id>.*)/$','delete_service_check',name="main_delete_service_check"),
                       url('^modal/check-form/$','modal_check_form',name="main_modal_check_form")
)

