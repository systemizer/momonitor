from django import forms
from momonitor.main.models import ServiceCheck


class ServiceCheckForm(forms.ModelForm):
    class Meta:
        model = ServiceCheck
