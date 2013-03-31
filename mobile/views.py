from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.contrib.auth.decorators import login_required
from momonitor.main.models import (Service,
                                   UmpireServiceCheck,
                                   SimpleServiceCheck,
                                   SensuServiceCheck,
                                   CompareServiceCheck,
                                   CodeServiceCheck,
                                   RESOURCE_NAME_MAP)

@login_required
def index(request):
    services = Service.objects.all().order_by("name")
    return render_to_response("mobile/index.html",
                              {'services':services},
                              RequestContext(request))

@login_required
def service(request,service_id):
    service = get_object_or_404(Service,pk=service_id)
    return render_to_response("mobile/service.html",
                              {'service':service},
                              RequestContext(request))

def check(request,check_name,check_id):
    if not RESOURCE_NAME_MAP.has_key(check_name):
        raise Http404    
    check_cls = RESOURCE_NAME_MAP[check_name]
    template_map = {
        SimpleServiceCheck:"simple_check.html",
        UmpireServiceCheck:"umpire_check.html",
        SensuServiceCheck:"sensu_check.html",
        CompareServiceCheck:"compare_check.html",
        CodeServiceCheck:"code_check.html"
        }
    template_file = template_map[check_cls]
    check = get_object_or_404(check_cls,pk=check_id)
    return render_to_response("mobile/checks/%s" % template_file,
                              {'check':check},
                              RequestContext(request))
