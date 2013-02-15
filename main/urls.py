from django.conf.urls.defaults import *
from momonitor.main.api import v1_api

urlpatterns = patterns('momonitor.main.views',
                       url('^$','index',name="main_index"),
                       url('^service/(?P<service_id>.*)/$','service',name="main_service"),                       
                       url('^refresh/(?P<resource_name>.*)/(?P<resource_id>.*)/$','refresh',name="main_refresh"),

                       #CRUD FORMS
                       url('^modal/form/(?P<resource_name>.*)/(?P<resource_id>.*)/$','modal_form',name="main_modal_form"),
                       url('^modal/form/(?P<resource_name>.*)/$','modal_form',name="main_modal_form"),

                       #Going to handle upload to code check manually because tastypie sucks at it
                       url(r'^api/v1/codeservicecheck/$','code_check_upload',name="main_code_check_upload"),
                       url(r'^api/v1/codeservicecheck/(?P<instance_id>.*)/$','code_check_upload',name="main_code_check_upload"),

                       #Test pagerduty functionality
                       url('^test/alert/(?P<service_id>.*)/$','test_alert',name="main_test_alert"),


                       (r'^api/', include(v1_api.urls)),
)

