from tastypie.resources import ModelResource
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from django.contrib.contenttypes.models import ContentType
from tastypie.authentication import Authentication
from tastypie import fields
from tastypie.authorization import Authorization
from momonitor.main.models import (Service,
                                   SimpleServiceCheck,
                                   UmpireServiceCheck,
                                   CompareServiceCheck,
                                   GraphiteServiceCheck,
                                   SensuServiceCheck,
                                   CodeServiceCheck)

from tastypie.api import Api

class CustomAuthentication(Authentication):
    def is_authenticated(self,request,**kwargs):
        if request.user.is_authenticated():
            return True
        return False

class ContentTypeResource(ModelResource):
    """
    Convenience model to represent ContentType model
    """
    # import here since otherwise importing TastyPie.resources will cause an
    # error unless django.contrib.contenttypes is enabled
    def __init__(self, *args, **kwargs):
        from django.contrib.contenttypes.models import ContentType
        self.Meta.queryset = ContentType.objects.all()
        self.Meta.object_class = self.Meta.queryset.model
        super(ContentTypeResource,self).__init__(*args, **kwargs)
        
    class Meta:
        resource_name = "objecttype"
        queryset = ContentType.objects.all()
        fields = ['model']
        detail_allowed_methods = ['get',]
        list_allowed_methods = ['get',]
    


class ServiceResource(ModelResource):
    class Meta:
        queryset = Service.objects.all()
        resource_name=Service.resource_name
        authorization=Authorization()
        authentication=CustomAuthentication()


class SimpleServiceCheckResource(ModelResource):
    service = fields.ToOneField(ServiceResource,'service')

    class Meta:
        queryset = SimpleServiceCheck.objects.all()
        resource_name=SimpleServiceCheck.resource_name
        authorization=Authorization()
        authentication=CustomAuthentication()

class GraphiteServiceCheckResource(ModelResource):
    service = fields.ToOneField(ServiceResource,'service')

    class Meta:
        queryset = GraphiteServiceCheck.objects.all()
        resource_name=GraphiteServiceCheck.resource_name
        authorization=Authorization()
        authentication=CustomAuthentication()

class SensuServiceCheckResource(ModelResource):
    service = fields.ToOneField(ServiceResource,'service')

    class Meta:
        queryset = SensuServiceCheck.objects.all()
        resource_name=SensuServiceCheck.resource_name
        authorization=Authorization()
        authentication=CustomAuthentication()

class CodeServiceCheckResource(ModelResource):
    service = fields.ToOneField(ServiceResource,'service')

    class Meta:
        queryset = CodeServiceCheck.objects.all()
        resource_name=CodeServiceCheck.resource_name
        authorization=Authorization()
        authentication=CustomAuthentication()

class CompareServiceCheckResource(ModelResource):
    service = fields.ToOneField(ServiceResource,'service')

    class Meta:
        queryset = CompareServiceCheck.objects.all()
        resource_name=CompareServiceCheck.resource_name
        authorization=Authorization()
        authentication=CustomAuthentication()

class UmpireServiceCheckResource(ModelResource):
    service = fields.ToOneField(ServiceResource,'service')

    class Meta:
        queryset = UmpireServiceCheck.objects.all()
        resource_name=UmpireServiceCheck.resource_name
        authorization=Authorization()
        authentication=CustomAuthentication()


v1_api = Api(api_name='v1')
v1_api.register(ServiceResource())
v1_api.register(SimpleServiceCheckResource())
v1_api.register(UmpireServiceCheckResource())
v1_api.register(CompareServiceCheckResource())
v1_api.register(SensuServiceCheckResource())
v1_api.register(CodeServiceCheckResource())
v1_api.register(GraphiteServiceCheckResource())
v1_api.register(ContentTypeResource())
