from momonitor.main.models import UmpireServiceCheck
from momonitor.main.forms.service_check import ServiceCheckForm

class UmpireServiceCheckForm(ServiceCheckForm):
    title="Create/Edit Umpire Checks"
    template="main/modal_forms/umpire_check.html"
    class Meta:
        model = UmpireServiceCheck
