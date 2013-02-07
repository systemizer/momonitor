from django import forms
from momonitor.main.models import (SimpleServiceCheck, 
                                   UmpireServiceCheck, 
                                   CompareServiceCheck,
                                   Service)

class UmpireServiceCheckForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(UmpireServiceCheckForm,self).__init__(*args,**kwargs)
        self.fields['description'].widget.attrs['rows'] = 5

    class Meta:
        model = UmpireServiceCheck

class CompareServiceCheckForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(CompareServiceCheckForm,self).__init__(*args,**kwargs)
        self.fields['description'].widget.attrs['rows'] = 5

    class Meta:
        model = CompareServiceCheck

class SimpleServiceCheckForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super(SimpleServiceCheckForm,self).__init__(*args,**kwargs)
        self.fields['description'].widget.attrs['rows'] = 5

    class Meta:
        model = SimpleServiceCheck

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
