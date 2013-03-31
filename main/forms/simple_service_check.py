from momonitor.main.models import SimpleServiceCheck
from momonitor.main.forms.service_check import ServiceCheckForm

class SimpleServiceCheckForm(ServiceCheckForm):
    title="Create/Edit Simple Checks"
    template="main/modal_forms/simple_check.html"
    class Meta:
        model = SimpleServiceCheck
