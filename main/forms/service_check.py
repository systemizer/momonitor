from django import forms
from momonitor.common.decorators import ClassProperty


class ServiceCheckForm(forms.ModelForm):
    @ClassProperty
    @classmethod
    def title(cls):
        return "Create/Edit %s Resources" % cls._meta.model.resource_name

    template="main/modal_forms/servicecheck.html"
    enctype = None
    service = forms.CharField(widget=forms.HiddenInput(attrs={'readonly':True}))

    def __init__(self,*args,**kwargs):
        service_id = kwargs.pop("service_id","")
        super(ServiceCheckForm,self).__init__(*args,**kwargs)
        if service_id:
            self.fields['service'].widget.attrs['value'] = service_id
        self.fields['description'].widget.attrs['rows'] = 5
        self.fields['description'].widget.attrs['placeholder'] = "Enter brief description here..."
        self.fields['name'].widget.attrs['placeholder'] = "Check Name"
        self.fields['failures_before_alert'].widget.attrs['placeholder'] = "i.e. 1"
        self.fields['frequency'].widget.attrs['placeholder'] = "i.e. */5 * * * *"
        if self.fields.has_key("endpoint"):
            self.fields['endpoint'].widget.attrs['placeholder'] = "http://example.org"
        if self.fields.has_key("timeout"):
            self.fields['timeout'].widget.attrs['placeholder'] = "i.e. 100"
        



