from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from momonitor.common.decorators import login_required
from momonitor.main.models import Service

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
