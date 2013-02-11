from django.conf.urls.defaults import *
from momonitor.main.api import v1_api

urlpatterns = patterns('momonitor.main.views',
                       url('^$','index',name="main_index"),
                       url('^service/(?P<service_id>.*)/$','service',name="main_service"),                       
                       url('^refresh/(?P<resource_name>.*)/(?P<resource_id>.*)/$','refresh',name="main_refresh"),

                       #CRUD FORMS
                       url('^modal/form/(?P<resource_name>.*)/(?P<resource_id>.*)/$','modal_form',name="main_modal_form"),
                       url('^modal/form/(?P<resource_name>.*)/$','modal_form',name="main_modal_form"),

                       #Test pagerduty functionality
                       url('^test/pagerduty/(?P<service_id>.*)/$','test_pagerduty',name="main_test_pagerduty"),


                       (r'^api/', include(v1_api.urls)),
)

