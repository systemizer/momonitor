from momonitor.main.models import CodeServiceCheck
from django import forms

class CodeServiceCheckForm(forms.ModelForm):
    enctype = "multipart/form-data"
    title="Create/Edit Code Checks"
    template="main/modal_forms/codeservicecheck.html"
    
    def __init__(self,*args,**kwargs):
        service_id = kwargs.pop("service_id","")
        super(CodeServiceCheckForm,self).__init__(*args,**kwargs)
        self.fields['service'].widget.attrs['class']="hide"
        self.fields['service'].widget.attrs['readonly']=True
        self.fields['description'].widget.attrs['rows'] = 5
        self.fields['description'].widget.attrs['placeholder'] = "Enter brief description here..."

    class Meta:
        model = CodeServiceCheck
