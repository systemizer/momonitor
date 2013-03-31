from momonitor.main.forms.service_check import ServiceCheckForm

def generate_check_modelform_cls(model_cls):
    class CheckForm(ServiceCheckForm):
        class Meta:
            model = model_cls

    return CheckForm
    
