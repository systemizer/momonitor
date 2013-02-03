from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse


from momonitor.main.models import Service, SimpleServiceCheck,UmpireServiceCheck
from momonitor.main.forms import (UmpireServiceCheckForm,
                                  SimpleServiceCheckForm,
                                  ServiceForm)
from momonitor.main.decorators import ajax_required

def index(request):
    services = Service.objects.all()
    return render_to_response("index.html",{'services':services},RequestContext(request))

def service(request,service_id):
    service = get_object_or_404(Service,pk=service_id)

    request.breadcrumbs("Services",reverse("main_index"))
    request.breadcrumbs(service.name,reverse("main_service",kwargs={'service_id':service.id}))

    return render_to_response("service.html",{'service':service},RequestContext(request))

def modal_form(request,resource_name,resource_id=None):
    resource_form_cls = {'service':ServiceForm,
                         'simpleservicecheck':SimpleServiceCheckForm,
                         'umpireservicecheck':UmpireServiceCheckForm}[resource_name]
    resource_cls = resource_form_cls._meta.model

    if resource_id:
        instance = get_object_or_404(resource_cls,pk=resource_id)
        method="PUT"
    else:
        instance = None
        method="POST"

    form = resource_form_cls(instance=instance)
    
    action = "/api/v1/%s/" % resource_cls.resource_name
    if instance:
        action+="%s/" % instance.id
    action+="?format=json"
        
    return render_to_response("modal_form.html",{"form":form,"action":action,'method':method},RequestContext(request))



'''These checks will refresh the check. should be ajax'''

@ajax_required
def refresh_service(request,service_id):    
    service = get_object_or_404(Service,pk=service_id)
    for check in service.all_checks():
        check.update_status()
    return HttpResponse("OK")

@ajax_required
def refresh_simple_check(request,check_id):    
    check = get_object_or_404(SimpleServiceCheck,pk=check_id)
    check.update_status()
    return HttpResponse("OK")

@ajax_required
def refresh_umpire_check(request,check_id):    
    check = get_object_or_404(UmpireServiceCheck,pk=check_id)
    check.update_status()
    return HttpResponse("OK")

