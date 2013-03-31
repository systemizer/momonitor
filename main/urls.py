from django.conf.urls.defaults import *
from momonitor.main.api import v1_api

urlpatterns = patterns('momonitor.main.views',
                       url('^$','index',name="index"),
                       url('^service/(?P<service_id>.*)/$','service',name="service"),                       
                       url('^refresh/(?P<resource_name>.*)/(?P<resource_id>.*)/$','refresh',name="refresh"),
                       url('^silence/(?P<resource_name>.*)/(?P<resource_id>.*)/$','silence',name="silence"),
                       url('^how-it-works/$','how_it_works',name="how_it_works"),

                       #CRUD FORMS
                       url('^modal/form/(?P<resource_name>.*)/(?P<resource_id>.*)/$','modal_form',name="modal_form"),
                       url('^modal/form/(?P<resource_name>.*)/$','modal_form',name="modal_form"),

                       #Going to handle upload to code check manually because tastypie sucks at it
                       url(r'^api/v1/codeservicecheck/$','code_check_upload',name="code_check_upload"),
                       url(r'^api/v1/codeservicecheck/(?P<instance_id>.*)/$','code_check_upload',name="code_check_upload"),

                       #Temporary sensu handler until backbone comes in
                       url('^sensu-check-info/(?P<sensu_check_id>.*)/$','sensu_check_info',name="sensu_check_info"),


                       (r'^api/', include(v1_api.urls))
)

