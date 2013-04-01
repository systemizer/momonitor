from momonitor.main.models import CompareServiceCheck
from momonitor.main.forms.service_check import ServiceCheckForm

class CompareServiceCheckForm(ServiceCheckForm):
    title="Create/Edit Compare Checks"
    template="main/modal_forms/compareservicecheck.html"
    class Meta:
        model = CompareServiceCheck

    def __init__(self,*args,**kwargs):
        super(CompareServiceCheckForm,self).__init__(*args,**kwargs)
        self.fields['comparator'].widget.attrs['style'] = "width:100px"
        self.fields['compared_value'].widget.attrs['style'] = "width:100px"
