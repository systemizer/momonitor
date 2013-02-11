from django import forms
import pdb
from momonitor.main.models import (SimpleServiceCheck, 
                                   UmpireServiceCheck, 
                                   CompareServiceCheck,
                                   ComplexServiceCheck,
                                   ComplexRelatedField,
                                   Service)

class ServiceCheckForm(forms.ModelForm):
    title = "Create/Edit Resources"
    service = forms.CharField(widget=forms.HiddenInput(attrs={'readonly':True}))
    def __init__(self,*args,**kwargs):
        service_id = kwargs.pop("service_id","")
        super(ServiceCheckForm,self).__init__(*args,**kwargs)
        if service_id:
            self.fields['service'].widget.attrs['value'] = service_id
        self.fields['description'].widget.attrs['rows'] = 5
        

class UmpireServiceCheckForm(ServiceCheckForm):
    title="Create/Edit Umpire Checks"
    class Meta:
        model = UmpireServiceCheck

class CompareServiceCheckForm(ServiceCheckForm):
    title="Create/Edit Compare Checks"
    class Meta:
        model = CompareServiceCheck

class SimpleServiceCheckForm(ServiceCheckForm):
    title="Create/Edit Simple Checks"
    class Meta:
        model = SimpleServiceCheck

class ComplexServiceCheckForm(ServiceCheckForm):
    title="Create/Edit Complex Check"
    class Meta:
        model = ComplexServiceCheck

class ComplexRelatedForm(forms.ModelForm):
    complex_check = forms.CharField(widget=forms.HiddenInput(attrs={'readonly':True}))
    def __init__(self,*args,**kwargs):
        complex_check_id = kwargs.pop("complex_service_id")
        super(ComplexRelatedForm,self).__init__(*args,**kwargs)
        if complex_check_id:
            self.fields['complex_check'].widget.attrs['value'] = complex_check_id
                                    
    title = "Add Rule to Complex Check"
    class Meta:
        model = ComplexRelatedField

class ServiceForm(forms.ModelForm):
    title="Create/Edit Service"
    class Meta:
        model = Service

RESOURCE_FORM_MAP = {
    Service:ServiceCheckForm,
    UmpireServiceCheck:UmpireServiceCheckForm,
    SimpleServiceCheck:SimpleServiceCheckForm,
    ComplexServiceCheck:ComplexServiceCheckForm,
    CompareServiceCheck:CompareServiceCheckForm,
    ComplexRelatedField:ComplexRelatedForm,
    Service:ServiceForm
}
