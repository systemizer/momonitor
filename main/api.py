from tastypie.resources import ModelResource
from tastypie import fields
from momonitor.main.models import Service,SimpleServiceCheck,UmpireServiceCheck
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

class UmpireServiceCheckResource(ModelResource):
    service = fields.ToOneField(ServiceResource,'service')

    class Meta:
        queryset = UmpireServiceCheck.objects.all()
        resource_name=UmpireServiceCheck.resource_name
        authorization=Authorization()
