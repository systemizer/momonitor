from momonitor.main.forms.service_check import ServiceCheckForm

def generate_check_modelform_cls(model_cls,template_path=None):
    class CheckForm(ServiceCheckForm):
        title="Create/Edit %s " % model_cls.__name__
        template = template_path or "main/modal_forms/servicecheck.html"
        class Meta:
            model = model_cls

    return CheckForm
    
