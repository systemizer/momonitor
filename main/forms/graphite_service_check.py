from momonitor.main.models import GraphiteServiceCheck
from momonitor.main.forms.service_check import ServiceCheckForm

class GraphiteServiceCheckForm(ServiceCheckForm):
    title="Create/Edit Graphite Checks"
    template="main/modal_forms/graphite_check.html"
    class Meta:
        model = GraphiteServiceCheck
