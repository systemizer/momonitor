from tastypie.resources import ModelResource
from tastypie.authentication import Authentication
from tastypie import fields
from tastypie.authorization import Authorization
from momonitor.main.models import (Service,
                                   CHECK_MODELS)

from tastypie.api import Api

class CustomAuthentication(Authentication):
    def is_authenticated(self,request,**kwargs):
        if request.user.is_authenticated():
            return True
        return False

v1_api = Api(api_name='v1')

class ServiceResource(ModelResource):
    class Meta:
        queryset = Service.objects.all()
        resource_name = Service.resource_name
        authorization = Authorization()
        authentication = CustomAuthentication()

v1_api.register(ServiceResource())

for check_cls in CHECK_MODELS:
    class CheckResource(ModelResource):
        service = fields.ToOneField(ServiceResource,'service')
        class Meta:
            queryset = check_cls.objects.all()
            resource_name=check_cls.resource_name
            authorization=Authorization()
            authentication=CustomAuthentication()

    v1_api.register(CheckResource())
