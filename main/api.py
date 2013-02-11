from tastypie.resources import ModelResource
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from django.contrib.contenttypes.models import ContentType
from tastypie import fields
from tastypie.authorization import Authorization
from momonitor.main.models import (Service,
                                   SimpleServiceCheck,
                                   UmpireServiceCheck,
                                   CompareServiceCheck,
                                   ComplexServiceCheck,
                                   ComplexRelatedField)

from tastypie.api import Api

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


class SimpleServiceCheckResource(ModelResource):
    service = fields.ToOneField(ServiceResource,'service')

    class Meta:
        queryset = SimpleServiceCheck.objects.all()
        resource_name=SimpleServiceCheck.resource_name
        authorization=Authorization()

class CompareServiceCheckResource(ModelResource):
    service = fields.ToOneField(ServiceResource,'service')

    class Meta:
        queryset = CompareServiceCheck.objects.all()
        resource_name=CompareServiceCheck.resource_name
        authorization=Authorization()

class UmpireServiceCheckResource(ModelResource):
    service = fields.ToOneField(ServiceResource,'service')

    class Meta:
        queryset = UmpireServiceCheck.objects.all()
        resource_name=UmpireServiceCheck.resource_name
        authorization=Authorization()

class ComplexServiceCheckResource(ModelResource):
    service = fields.ToOneField(ServiceResource,'service')

    class Meta:
        queryset = ComplexServiceCheck.objects.all()
        resource_name=ComplexServiceCheck.resource_name
        authorization=Authorization()

class ComplexRelatedFieldResource(ModelResource):
    check = GenericForeignKeyField({
            SimpleServiceCheck:SimpleServiceCheckResource,
            CompareServiceCheck:CompareServiceCheckResource,
            UmpireServiceCheck:UmpireServiceCheckResource
            },"check")

    object_type = fields.ToOneField(ContentTypeResource,"object_type")
    complex_check = fields.ToOneField(ComplexServiceCheckResource,'complex_check')


    class Meta:
        resource_name=ComplexRelatedField.resource_name
        queryset = ComplexRelatedField.objects.all()
        authorization=Authorization()



v1_api = Api(api_name='v1')
v1_api.register(ServiceResource())
v1_api.register(SimpleServiceCheckResource())
v1_api.register(UmpireServiceCheckResource())
v1_api.register(CompareServiceCheckResource())
v1_api.register(ComplexServiceCheckResource())
v1_api.register(ComplexRelatedFieldResource())
v1_api.register(ContentTypeResource())
