from django import forms
import pdb
from momonitor.main.models import (SimpleServiceCheck, 
                                   UmpireServiceCheck, 
                                   CompareServiceCheck,
                                   ComplexServiceCheck,
                                   PastServiceCheck,
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
        self.fields['description'].widget.attrs['placeholder'] = "Enter brief description here..."
        

class UmpireServiceCheckForm(ServiceCheckForm):
    title="Create/Edit Umpire Checks"
    template="modal_forms/umpire_check.html"
    class Meta:
        model = UmpireServiceCheck

class PastServiceCheckForm(ServiceCheckForm):
    title="Create/Edit Past Checks"
    template="modal_forms/past_check.html"
    class Meta:
        model = PastServiceCheck

class CompareServiceCheckForm(ServiceCheckForm):
    title="Create/Edit Compare Checks"
    template="modal_forms/compare_check.html"
    class Meta:
        model = CompareServiceCheck

    def __init__(self,*args,**kwargs):
        super(CompareServiceCheckForm,self).__init__(*args,**kwargs)
        self.fields['comparator'].widget.attrs['style'] = "width:100px"
        self.fields['compared_value'].widget.attrs['style'] = "width:100px"

class SimpleServiceCheckForm(ServiceCheckForm):
    title="Create/Edit Simple Checks"
    template="modal_forms/simple_check.html"
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
    template="modal_forms/serviceform.html"
    class Meta:
        model = Service

RESOURCE_FORM_MAP = {
    Service:ServiceCheckForm,
    UmpireServiceCheck:UmpireServiceCheckForm,
    SimpleServiceCheck:SimpleServiceCheckForm,
    ComplexServiceCheck:ComplexServiceCheckForm,
    CompareServiceCheck:CompareServiceCheckForm,
    PastServiceCheck:PastServiceCheckForm,
    ComplexRelatedField:ComplexRelatedForm,
    Service:ServiceForm
}
