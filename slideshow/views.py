from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from momonitor.main.models import Service
from momonitor.common.decorators import login_required

@login_required
def index(request):
    services = Service.objects.all()
    return render_to_response("slideshow/index.html",
                              {'services':services},
                              RequestContext(request))

@login_required
def view_slideshow(request,service_id):
    service = get_object_or_404(Service,pk=service_id)
    return render_to_response("slideshow/slideshow.html",
                              {'service':service},
                              RequestContext(request))
