from tastypie.resources import ModelResource
from tastypie import fields
from momonitor.main.models import (Service,
                                   SimpleServiceCheck,
                                   UmpireServiceCheck,
                                   CompareServiceCheck,
                                   ComplexServiceCheck,
                                   ComplexRelatedField)

from tastypie.authorization import Authorization

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

    class Meta:
        resource_name=ComplexRelatedField.resource_name
        queryset = ComplexRelatedField.objects.all()
        authorization=Authorization()
