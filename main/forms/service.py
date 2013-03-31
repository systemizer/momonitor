from django import forms
from momonitor.main.models import Service

class ServiceForm(forms.ModelForm):
    title="Create/Edit Service"
    template="main/modal_forms/serviceform.html"
    class Meta:
        model = Service
