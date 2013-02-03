from django import forms
from momonitor.main.models import ServiceCheck, Service


class ServiceCheckForm(forms.ModelForm):
    class Meta:
        model = ServiceCheck

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
