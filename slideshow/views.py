from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from momonitor.main.models import Service
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings

from django.contrib.auth.decorators import login_required as _login_required

###django-social-auth does a terrible job allowing for unitests. 
###I rather just skip the whole process
def login_required(function=None,
                   redirect_field_name=REDIRECT_FIELD_NAME,
                   login_url=None):
    if settings.TESTING:
        return function
    else:
        return _login_required(function,redirect_field_name,login_url)

####
# VIEWS
####

@login_required
def index(request):
    services = Service.objects.all()
    return render_to_response("slideshow-index.html",
                              {'services':services},
                              RequestContext(request))

@login_required
def view_slideshow(request,service_id):
    service = get_object_or_404(Service,pk=service_id)
    return render_to_response("slideshow.html",
                              {'service':service},
                              RequestContext(request))
