from momonitor.main.models import SensuServiceCheck
from momonitor.main.forms.service_check import ServiceCheckForm

class SensuServiceCheckForm(ServiceCheckForm):
    title="Create/Edit Sensu Checks"
    template="main/modal_forms/sensu_check.html"
    class Meta:
        model = SensuServiceCheck

