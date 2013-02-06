from django.conf.urls.defaults import *
from momonitor.main.api import (ServiceResource,
                                SimpleServiceCheckResource,
                                UmpireServiceCheckResource,)
from tastypie.api import Api

v1_api = Api(api_name='v1')
v1_api.register(ServiceResource())
v1_api.register(SimpleServiceCheckResource())
v1_api.register(UmpireServiceCheckResource())

urlpatterns = patterns('momonitor.main.views',
                       url('^$','index',name="main_index"),
                       url('^service/(?P<service_id>.*)/$','service',name="main_service"),
                       
                       #refresh handlers
                       url('^refresh/service/(?P<service_id>.*)/$','refresh_service',name="main_refresh_service"),
                       url('^refresh/simplecheck/(?P<check_id>.*)/$','refresh_simple_check',name="main_refresh_simple_check"),
                       url('^refresh/umpirecheck/(?P<check_id>.*)/$','refresh_umpire_check',name="main_refresh_umpire_check"),

                       #CRUD FORMS
                       url('^modal/form/(?P<resource_name>.*)/(?P<resource_id>.*)/$','modal_form',name="main_modal_form"),
                       url('^modal/form/(?P<resource_name>.*)/$','modal_form',name="main_modal_form"),

                       #Test pagerduty functionality
                       url('^test/pagerduty/(?P<service_id>.*)/$','test_pagerduty',name="main_test_pagerduty"),


                       (r'^api/', include(v1_api.urls)),
)

