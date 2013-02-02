from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib import messages


from momonitor.main.models import Service, ServiceCheck
from momonitor.main.forms import ServiceCheckForm

def index(request):
    services = Service.objects.all()
    return render_to_response("index.html",{'services':services},RequestContext(request))

def service(request,service_id):
    service = get_object_or_404(Service,pk=service_id)

    request.breadcrumbs("Services",reverse("main_index"))
    request.breadcrumbs(service.name,reverse("main_service",kwargs={'service_id':service.id}))



    # then look for add check post request
    if request.method=="POST":
        if request.GET.get("service_check_id"):
            instance = get_object_or_404(ServiceCheck,pk=request.GET.get("service_check_id"))
        else:
            instance = None

        form = ServiceCheckForm(request.POST,instance=instance)

        if form.is_valid():
            check = form.save()
            messages.success(request,"New Check Created!",extra_tags='alert-success')
        else:
            messages.error(request,"Failed to create new check",extra_tags="alert-error")

    form = ServiceCheckForm()
    return render_to_response("service.html",{'service':service,
                                              'form':form},
                              RequestContext(request))

def modal_check_form(request):
    if request.GET.get("service_check_id"):
        instance = get_object_or_404(ServiceCheck,pk=request.GET.get("service_check_id"))
    else:
        instance = None

    form = ServiceCheckForm(instance=instance)
    return render_to_response("modals/check-form.html",{'form':form,
                                                        'instance':instance},RequestContext(request))
        

def refresh_service(request,service_id):
    service = get_object_or_404(Service,pk=service_id)
    service.run_checks()
    return redirect(reverse("main_service",kwargs={'service_id':service_id}))

def delete_service_check(request,service_check_id):
    service_check = get_object_or_404(ServiceCheck,pk=service_check_id)
    service_check.delete()
    return redirect(reverse("main_service",kwargs={'service_id':service_check.service.id}))
